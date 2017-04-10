import traceback
import schedule
import time

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from django.conf import settings
from mnm.instances import tasks


class Command(BaseCommand):
    help = 'Fetch instance data regularly'

    def handle(self, *args, **options):
        schedule.every(settings.FETCH_DELAY).seconds.do(tasks.fetch_instances)

        self.stdout.write(self.style.SUCCESS('Starting job runner...'))
        while True:
            time.sleep(1)
            try:
                schedule.run_pending()
            except:
                traceback.print_exc()
