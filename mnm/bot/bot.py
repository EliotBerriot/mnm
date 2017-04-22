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
