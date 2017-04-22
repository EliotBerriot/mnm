import time
from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from mnm.statuses import record
from mnm import client


class Command(BaseCommand):
    help = 'record public timeline of an instance using the streaming API'

    def handle(self, *args, **options):

        while True:
            print('Initiating connection...')
            try:
                client = client.get_client(
                    client_id=settings.STATUSES_RECORD['client_id'],
                    client_secret=settings.STATUSES_RECORD['client_secret'],
                    access_token=settings.STATUSES_RECORD['access_token'],
                    api_base_url=settings.STATUSES_RECORD['api_base_url'],
                )
                record.record_public_status(client)
            except ValueError as e:
                print(e)
                print('Will reconnect in 10 seconds...')
                time.sleep(10)
