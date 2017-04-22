import time
from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
import mastodon

class Command(BaseCommand):
    help = 'Register an app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='mnm',
            dest='name',
            help='App identifier that will be used on the matodon instance'
        )
        parser.add_argument(
            'url',
            type=str,
            help='URL of the mastodon instance you want to register the app on',
        )

    def handle(self, *args, **options):

        cid, csec = mastodon.Mastodon.create_app(
             options['name'],
             api_base_url=options['url'],
        )

        self.stdout.write(
            self.style.SUCCESS('Registered app {} on {}'.format(
                options['name'], options['url'])))
        self.stdout.write(
            self.style.SUCCESS('Put the following variables in your .env file'))
        self.stdout.write(
            self.style.SUCCESS('(prefix them with STATUSES_RECORD_ or STATS_BOT_)'))
        self.stdout.write(('CLIENT_ID={}'.format(cid)))
        self.stdout.write(('CLIENT_SECRET={}'.format(csec)))
        self.stdout.write(('URL={}'.format(options['url'])))
