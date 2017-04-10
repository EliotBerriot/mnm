from django.db import models


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
