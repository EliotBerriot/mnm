from django.conf import settings
from django.utils.html import strip_tags
import mastodon

from mnm import client

from . import commands


from mnm.statuses import tasks


class BotListener(mastodon.StreamListener):
    def __init__(self, bot):
        self.bot = bot

    def on_notification(self, notification):
        from . import tasks
        if notification['type'] != 'mention':
            return

        tasks.reply.apply_async(args=(notification['status'],))


class Bot(object):
    def __init__(self):
        self.name = settings.STATS_BOT['name']
        self.client = client.get_client(
            client_id=settings.STATS_BOT['client_id'],
            client_secret=settings.STATS_BOT['client_secret'],
            access_token=settings.STATS_BOT['access_token'],
            api_base_url=settings.STATS_BOT['api_base_url']
        )

    def publish(self, status, visibility='private', in_reply_to_id=None):
        return self.client.status_post(
            status,
            visibility=visibility,
            in_reply_to_id=in_reply_to_id,
        )

    def parse(self, status):
        real_command = [
            w for w in status.split(' ')
            if '@' not in w
        ]
        try:
            command = real_command[0]
        except IndexError:
            return 'help', []

        # non-slash messages are ignored
        if not command.startswith('/'):
            if command == 'help':
                # fallback to help
                return 'help', []
            return None, []

        # remove the slash
        command = command[1:]
        arguments = real_command[1:]

        return command, arguments

    def get_response(self, status, reraise=False):
        content = strip_tags(status['content'])
        command, arguments = self.parse(content)
        if command is None:
            return
        try:
            handler = commands.commands[command]
        except KeyError:
            handler = commands.commands['unknown']
        sender = status['account']['acct']
        try:
            response_content = handler.handle(sender, *arguments)
        except Exception as e:
            if reraise:
                raise
            handler = commands.commands['error']
            response_content = handler.handle(sender, *arguments)
        mentions = [
            '@{}'.format(m['acct'])
            for m in status['mentions']
            if m['acct'].split('@')[0] != self.name.split('@')[0]
        ]
        mentions = ['@{}'.format(sender)] + mentions
        final_content = '{}\n{}'.format(
            ' '.join(mentions),
            response_content,
        )
        return {
            'status': final_content,
            'in_reply_to_id': status['id'],
            'visibility': status['visibility'],
        }

    def handle(self, status):
        response = self.get_response(status)
        if response is None:
            return
        return response, self.publish(**response)

    def listen(self):
        self.client.user_stream(BotListener(self))
