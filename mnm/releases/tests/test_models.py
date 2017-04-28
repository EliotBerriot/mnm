import os
import unittest
import datetime
import requests_mock
from test_plus.test import TestCase

from django.utils import timezone
from django.db import IntegrityError, transaction

from mnm.releases import models
from mnm.releases import parsers


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')


class TestModels(TestCase):

    def test_can_create_release(self):
        r = models.Release.objects.create(
            tag='v1.2',
            url='http://test.yolo/release',
            release_date=timezone.now(),
        )
        self.assertEqual(r.version_major, 1)
        self.assertEqual(r.version_minor, 2)
        self.assertEqual(r.version_patch, 0)
        self.assertEqual(r._version, '00001.00002.00000')

    def test_conflictig_releases(self):
        r = models.Release.objects.create(
            tag='v1.2',
            url='http://test.yolo/release1',
            release_date=timezone.now(),
        )
        with transaction.atomic(), self.assertRaises(IntegrityError):
            models.Release.objects.create(
                tag='v1.2',
                url='http://test.yolo/release2',
                release_date=timezone.now(),
            )

    @requests_mock.mock()
    def test_can_fetch_releases_from_github_api(self, m):
        html = os.path.join(DATA_DIR, 'releases.json')
        with open(html) as f:
            content = f.read()

        m.get(parsers.RELEASES_URL, text=content)
        results = parsers.fetch_releases()

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['tag_name'], 'v1.3.1')
        self.assertEqual(results[0]['prerelease'], False)

        self.assertEqual(results[1]['tag_name'], 'v1.3')
        self.assertEqual(results[1]['prerelease'], False)

    def test_can_import_releases(self):
        now = timezone.now()
        yesterday = now - datetime.timedelta(days=1)
        releases_data = [
            {
                "url": "https://api.github.com/repos/tootsuite/mastodon/releases/6215456",
                "html_url": "https://github.com/tootsuite/mastodon/releases/tag/v1.3.1",
                "tag_name": "v1.3.1",
                "name": "v1.3.1",
                "draft": False,
                "prerelease": False,
                "created_at": now,
                "published_at": now,
                "body": "Hello world 1"
            },
            {
                "url": "https://api.github.com/repos/tootsuite/mastodon/releases/6210603",
                "html_url": "https://github.com/tootsuite/mastodon/releases/tag/v1.3",
                "tag_name": "v1.3",
                "name": "v1.3",
                "draft": False,
                "prerelease": False,
                "created_at": yesterday,
                "published_at": yesterday,
                "body": "Hello world 2"
            }
        ]

        releases = parsers.import_releases(releases_data)

        self.assertEqual(models.Release.objects.count(), 2)

        v131 = models.Release.objects.get(tag='v1.3.1')
        v130 = models.Release.objects.get(tag='v1.3')

        self.assertEqual(v131.url, releases_data[0]['html_url'])
        self.assertEqual(v131.creation_date, releases_data[0]['created_at'])
        self.assertEqual(v131.release_date, releases_data[0]['published_at'])
        self.assertEqual(v131.body, releases_data[0]['body'])

        self.assertEqual(v130.url, releases_data[1]['html_url'])
        self.assertEqual(v130.creation_date, releases_data[1]['created_at'])
        self.assertEqual(v130.release_date, releases_data[1]['published_at'])
        self.assertEqual(v130.body, releases_data[1]['body'])

    def test_can_import_releases_updating_existing(self):
        now = timezone.now()
        release = models.Release.objects.create(
            tag='v1.3.1',
            url='http://wrong.url',
            body='nope',
            release_date=now,
        )
        releases_data = [
            {
                "url": "https://api.github.com/repos/tootsuite/mastodon/releases/6215456",
                "html_url": "https://github.com/tootsuite/mastodon/releases/tag/v1.3.1",
                "tag_name": "v1.3.1",
                "name": "v1.3.1",
                "draft": False,
                "prerelease": False,
                "created_at": now,
                "published_at": now,
                "body": "Hello world 1"
            },
        ]

        releases = parsers.import_releases(releases_data)

        self.assertEqual(models.Release.objects.count(), 1)

        release.refresh_from_db()

        self.assertEqual(release.url, releases_data[0]['html_url'])
        self.assertEqual(release.creation_date, releases_data[0]['created_at'])
        self.assertEqual(release.release_date, releases_data[0]['published_at'])
        self.assertEqual(release.body, releases_data[0]['body'])

    def test_creating_a_recent_new_release_will_send_a_toot(self):

        with self.settings(NOTIFY_ON_RELEASE=True):
            with unittest.mock.patch('mnm.bot.bot.Bot.publish') as m:
                i1 = models.Release.objects.create(
                    tag='1.2',
                    url='http://test.release1',
                    release_date=timezone.now(),
                )
                kwargs = {
                    'status': i1.RELEASE_MESSAGE.format(
                        tag=i1.tag, url=i1.url),
                    'visibility': 'public',
                }
                m.assert_called_once_with(**kwargs)
