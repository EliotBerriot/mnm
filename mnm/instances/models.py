import geohash

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

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    country_code = models.CharField(null=True, blank=True, max_length=5)
    region_code = models.CharField(null=True, blank=True, max_length=5)

    # it's sad, but some instances start reporting fake numbers,
    # see https://github.com/EliotBerriot/mnm/issues/8
    is_blocked = models.BooleanField(default=False)

    @property
    def url(self):
        return 'https://{}'.format(self.name)

    @property
    def geohash(self):
        if not self.latitude or not self.longitude:
            return

        return geohash.encode(self.latitude, self.longitude, precision=3)

    def push_to_influxdb(self):
        return influxdb_client.push([self.to_influxdb()])

    def import_geoip_data(self, data):
        from . import parsers
        tld_country = parsers.fetch_country_from_tld(self.name)

        self.latitude = data['latitude']
        self.longitude = data['longitude']
        self.country_code = tld_country or data['country_code']
        self.region_code = data['region_code']

    def to_influxdb(self, table='instances', time=None):
        if not time:
            try:
                time = self.last_fetched
            except AttributeError:
                time = timezone.now()
        return {
            "measurement": table,
            "time": time.isoformat(),
            "tags": {
                'open_registrations': self.open_registrations,
                'up': self.up,
                'https_rank': self.https_rank,
                'ipv6': self.ipv6,
                'name': self.name,
                'country_code': self.country_code,
                'region_code': self.region_code,
                'geohash': self.geohash,
            },
            "fields": {
                '_quantity': 1,
                'https_score': self.https_score,
                'statuses': self.statuses,
                'users': self.users,
                'connections': self.connections,
            },
        }
