from django.db import models

from . import influxdb_client


class Instance(models.Model):
    name = models.CharField(unique=True, max_length=255, db_index=True)
    last_fetched = models.DateTimeField(null=True, blank=True)

    # date recorded when last fetching
    users = models.PositiveIntegerField(null=True, blank=True)
    statuses = models.PositiveIntegerField(null=True, blank=True)
    connections = models.PositiveIntegerField(null=True, blank=True)
    open_registrations = models.NullBooleanField(null=True, blank=True)
    up = models.NullBooleanField(null=True, blank=True)
    ipv6 = models.NullBooleanField(null=True, blank=True)
    https_score = models.PositiveIntegerField(null=True, blank=True)
    https_rank = models.CharField(null=True, blank=True, max_length=10)

    @property
    def url(self):
        return 'https://{}'.format(self.name)

    def push_to_influxdb(self):
        return influxdb_client.push([self.to_influxdb()])

    def to_influxdb(self, time=None):
        if not time:
            try:
                time = self.last_fetched
            except AttributeError:
                time = timezone.now()
        return {
            "measurement": "instances",
            "time": time.isoformat(),
            "tags": {
                'open_registrations': self.open_registrations,
                'up': self.up,
                'https_rank': self.https_rank,
                'ipv6': self.ipv6,
                'name': self.name,
            },
            "fields": {
                '_quantity': 1,
                'https_score': self.https_score,
                'statuses': self.statuses,
                'users': self.users,
                'connections': self.connections,
            },
        }
