import geohash

from django.db import models
from django.utils import timezone
from dynamic_preferences.registries import global_preferences_registry

from . import influxdb_client
from . import countries


class InstanceQuerySet(models.QuerySet):

    def public(self):
        return self.exclude(is_blocked=True)


class Instance(models.Model):
    name = models.CharField(unique=True, max_length=255, db_index=True)
    last_fetched = models.DateTimeField(null=True, blank=True)
    creation_date = models.DateTimeField(default=timezone.now)

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
    region = models.CharField(null=True, blank=True, max_length=30)

    # it's sad, but some instances start reporting fake numbers,
    # see https://github.com/EliotBerriot/mnm/issues/8
    is_blocked = models.BooleanField(default=False)

    release = models.ForeignKey(
        'releases.Release', null=True, blank=True, related_name='instances')

    # activity stats
    last_week_statuses = models.PositiveIntegerField(null=True, blank=True)
    last_week_logins = models.PositiveIntegerField(null=True, blank=True)
    last_week_registrations = models.PositiveIntegerField(
        null=True, blank=True)
    objects = InstanceQuerySet.as_manager()

    @property
    def url(self):
        return 'https://{}'.format(self.name)

    def get_info_api_url(self):
        return 'https://{}/api/v1/instance'.format(self.name)

    @property
    def geohash(self):
        if not self.latitude or not self.longitude:
            return

        return geohash.encode(self.latitude, self.longitude, precision=3)

    @property
    def country_data(self):
        if not self.country_code:
            return {}
        return countries.get_country_data_from_code(self.country_code)

    def get_dashboard_url(self):
        global_preferences = global_preferences_registry.manager()
        base_url = global_preferences['instances__detail_dashboard_url']
        return base_url.format(instance=self.name)

    def push_to_influxdb(self):
        return influxdb_client.push([self.to_influxdb()])

    def to_influxdb(self, table='instances', time=None):
        if not time:
            try:
                time = self.last_fetchede
            except AttributeError:
                time = timezone.now()
        d = {
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
                'region': self.region,
                'geohash': self.geohash,
                'release_full': self.release.version_string if self.release else 'UNKNOWN',
                'release_major': self.release.version_major if self.release else 0,
                'release_minor': self.release.version_minor if self.release else 0,
                'release_patch': self.release.version_patch if self.release else 0,
            },
            "fields": {
                '_quantity': 1,
                'https_score': self.https_score,
                'statuses': self.statuses,
                'users': self.users,
                'connections': self.connections,
            },
        }
        for activity in ['registrations', 'statuses', 'logins']:
            key = 'last_week_{}'.format(activity)
            v = getattr(self, key)
            if v is not None:
                d['fields'][key] = v

        return d
