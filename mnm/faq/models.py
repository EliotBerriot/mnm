from django.db import models
import markdown
from django.utils import timezone


class EntryQuerySet(models.QuerySet):
    def public(self):
        return self.filter(status='published')


class Entry(models.Model):

    title = models.CharField(max_length=255)
    content = models.TextField()

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    status = models.CharField(choices=STATUS_CHOICES, default='draft', max_length=15)

    sort_order = models.PositiveIntegerField(default=0)
    last_modification_date = models.DateTimeField(auto_now=True)
    creation_date = models.DateTimeField(default=timezone.now)

    objects = EntryQuerySet.as_manager()

    class Meta:
        ordering = ('sort_order',)

    @property
    def content_rendered(self):
        return markdown.markdown(self.content)
