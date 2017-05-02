import markdown
import distutils.version
import datetime

from django.db.models.signals import post_save
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone
from mnm.bot.tasks import publish


def sortable_version(*parts):
    return '.'.join(str(bit).zfill(5) for bit in parts)


class ReleaseQuerySet(models.QuerySet):
    def get_from_version_string(self, v):
        parts = v.split('.')
        kw = {}
        kw['version_major'] = parts[0]
        kw['version_minor'] = parts[1]
        try:
            kw['version_patch'] = parts[2]
        except IndexError:
            kw['version_patch'] = 0
        return self.get(**kw)


class Release(models.Model):
    release_date = models.DateTimeField()
    creation_date = models.DateTimeField(default=timezone.now)
    tag = models.CharField(max_length=100, db_index=True)
    _version = models.CharField(max_length=255, db_index=True, blank=True)
    version_major = models.PositiveIntegerField(blank=True)
    version_minor = models.PositiveIntegerField(blank=True)
    version_patch = models.PositiveIntegerField(blank=True)

    url = models.URLField()
    body = models.TextField(null=True, blank=True, default='')

    RELEASE_MESSAGE = "Mastodon {tag} has been released, check it out!\n\n{url}\n\n #mastodon #release"

    objects = ReleaseQuerySet.as_manager()

    class Meta:
        unique_together = (
            'version_major',
            'version_minor',
            'version_patch',
        )
        ordering = ('-_version', )

    @property
    def content_rendered(self):
        return markdown.markdown(self.body)

    @property
    def version(self):
        tag = self.tag
        if tag.startswith('v'):
            tag = tag[1:]
        return distutils.version.StrictVersion(tag)

    @property
    def important_version(self):
        return '.'.join([str(self.version_major), str(self.version_minor)])

    @property
    def tuple_version(self):
        return (self.version_major, self.version_minor, self.version_patch)

    @property
    def version_string(self):
        return '{}.{}.{}'.format(*self.tuple_version)

    def save(self, **kwargs):
        self.version_major, self.version_minor, self.version_patch = self.version.version
        self._version = sortable_version(*self.tuple_version)

        super().save(**kwargs)


@receiver(post_save, sender=Release)
def notify_release_publicly(sender, instance, created, **kwargs):
    if not created or not settings.NOTIFY_ON_RELEASE:
        return

    if instance.release_date < timezone.now() - datetime.timedelta(hours=2):
        return
    return publish.delay(
        status=instance.RELEASE_MESSAGE.format(
            url=instance.url,
            tag=instance.tag,
        ),
        visibility='public',
    )
