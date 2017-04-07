from django.db import models


class Instance(models.Model):
    url = models.URLField(unique=True)
    last_fetched = models.DateTimeField(null=True, blank=True)

    # date recorded when last fetching
    users = models.PositiveIntegerField(null=True, blank=True)
    statuses = models.PositiveIntegerField(null=True, blank=True)
    connections = models.PositiveIntegerField(null=True, blank=True)
    open_registration = models.NullBooleanField(null=True, blank=True)
    up = models.NullBooleanField(null=True, blank=True)
