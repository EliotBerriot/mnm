import time
from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from mnm.bot import bot


class Command(BaseCommand):
    help = 'Start the stats bot'

    def handle(self, *args, **options):
        b = bot.Bot()
        while True:
            print('Initiating connection...')
            try:
                b.listen()
            except ValueError as e:
                print(e)
                print('Will reconnect in 10 seconds...')
                time.sleep(10)
