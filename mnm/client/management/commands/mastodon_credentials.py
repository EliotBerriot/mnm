import getpass
from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
import mastodon


class Command(BaseCommand):
    help = 'Register an app'

    def add_arguments(self, parser):
        parser.add_argument(
            'url',
            type=str,
            help='URL of the mastodon instance where you have the account you wnat to use',
        )
        parser.add_argument(
            'email',
            type=str,
            help='Mastodon account email',
        )
        parser.add_argument(
            'kind',
            type=str,
            help='What kind of credentials (stats_bot or statuses_record)?',
        )

    def handle(self, *args, **options):
        kinds = ['stats_bot', 'statuses_record']

        kind = options['kind']
        if kind not in kinds:
            raise ValueError('invalid value')

        kind = kind.upper()

        email = options['email']
        password = getpass.getpass('Mastodon account password? ')

        config = getattr(settings, kind)

        client = mastodon.Mastodon(
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            api_base_url=options['url'],

        )
        token = client.log_in(email, password, scopes=['read', 'write', 'follow'],)

        self.stdout.write(
            self.style.SUCCESS('Successfully logged in as {} on {}'.format(
                email, options['url'])))
        self.stdout.write(
            self.style.SUCCESS('Put the following variable in your .env file'))
        self.stdout.write(('{}_ACCESS_TOKEN={}'.format(kind, token)))
