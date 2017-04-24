from django.conf import settings

from mnm import client


class Bot(object):
    def __init__(self):
        self.client = client.get_client(
            client_id=settings.STATS_BOT['client_id'],
            client_secret=settings.STATS_BOT['client_secret'],
            access_token=settings.STATS_BOT['access_token'],
            api_base_url=settings.STATS_BOT['api_base_url']
        )

    def publish(self, status, visibility='public'):
        return self.client.status_post(
            status,
            visibility=visibility,
        )

    def parse(self, status):
        real_command = [
            w for w in status.split(' ')
            if '@' not in w
        ]
        try:
            command = real_command[0]
        except IndexError:
            return None, None

        # non-slash messages are ignored
        if not command.startswith('/'):
            return None, None

        # remove the slash
        command = command[1:]
        arguments = real_command[1:]

        return command, arguments
