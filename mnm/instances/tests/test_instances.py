import os
import unittest
import requests
import requests_mock
from test_plus.test import TestCase
from django.utils import timezone
from mnm.instances import models
from mnm.instances import parsers
from mnm.instances import countries
from mnm.instances import tasks
from mnm.releases.tests.factories import ReleaseFactory

from .factories import InstanceFactory

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')


class TestInstances(TestCase):

    def test_can_create_instance(self):
        instance = models.Instance.objects.create(
            name='test.io',
        )

        self.assertIsNone(instance.last_fetched)
        self.assertIsNone(instance.users)
        self.assertIsNone(instance.statuses)
        self.assertIsNone(instance.connections)
        self.assertIsNone(instance.open_registrations)
        self.assertIsNone(instance.up)
        self.assertIsNone(instance.https_score)
        self.assertIsNone(instance.ipv6)
        self.assertIsNone(instance.https_rank)

    @requests_mock.mock()
    def test_can_extract_instances_list_from_instances_xyz(self, m):
        html = os.path.join(DATA_DIR, 'instances.json')
        with open(html) as f:
            content = f.read()

        m.get('https://instances.social/api/1.0/instances/list?count=0', text=content)
        results = parsers.parser_instances_social()

        self.assertEqual(len(results['instances']), 2)
        self.assertEqual(results['instances'][0]['name'], 'mastodon.social')
        self.assertEqual(results['instances'][0]['users'], 330)
        self.assertEqual(results['instances'][0]['statuses'], 1132540)
        self.assertEqual(results['instances'][0]['connections'], 827)
        self.assertEqual(results['instances'][0]['open_registrations'], True)
        self.assertEqual(results['instances'][0]['up'], True)
        self.assertEqual(results['instances'][0]['ipv6'], False)
        self.assertEqual(results['instances'][0]['https_score'], 81)
        self.assertEqual(results['instances'][0]['https_rank'], "A")

        self.assertEqual(results['instances'][1]['name'], 'mastodon.xyz')
        self.assertEqual(results['instances'][1]['users'], 5627)
        self.assertEqual(results['instances'][1]['open_registrations'], False)
        self.assertEqual(results['instances'][1]['statuses'], 64678)
        self.assertEqual(results['instances'][1]['ipv6'], False)
        self.assertEqual(results['instances'][1]['up'], False)
        self.assertEqual(results['instances'][1]['connections'], 521)
        self.assertEqual(results['instances'][1]['https_score'], 96)
        self.assertEqual(results['instances'][1]['https_rank'], "A+")

    @requests_mock.mock()
    def test_can_get_or_create_instances_based_on_parse_results(self, m):
        existing = models.Instance.objects.create(
            name='mastodon.social',
        )
        html = os.path.join(DATA_DIR, 'instances.json')
        with open(html) as f:
            content = f.read()
        now = timezone.now()
        m.get('https://instances.social/api/1.0/instances/list?count=0', text=content)
        with unittest.mock.patch('django.utils.timezone.now', return_value=now):
            results = parsers.parser_instances_social()

        instances = parsers.import_results(
            results['instances'])

        expected = [
            {
                "name": "mastodon.social",
                "up": True,
                "https_score": 81,
                "https_rank": "A",
                "ipv6": False,
                "open_registrations": True,
                "users": 330,
                "statuses": 1132540,
                "last_fetched": now,
                "connections": 827},
            {
                "name": "mastodon.xyz",
                "up":  False,
                "https_score": 96,
                "https_rank": "A+",
                "ipv6": False,
                "open_registrations":  False,
                "users": 5627,
                "statuses": 64678,
                "last_fetched": now,
                "connections": 521},
        ]

        self.assertEqual(existing, instances[0])

        for i, instance in enumerate(instances):
            for key, value in expected[i].items():
                self.assertEqual(getattr(instance, key), value)

        # we can rerun the same method without duplicating instances
        with unittest.mock.patch('django.utils.timezone.now', return_value=now):
            results = parsers.parser_instances_social()
        instances = parsers.import_results(results['instances'])
        self.assertEqual(models.Instance.objects.count(), 2)
        for i, instance in enumerate(instances):
            for key, value in expected[i].items():
                self.assertEqual(getattr(instance, key), value)

    def test_can_serialize_instance_to_influxdb(self):
        now = timezone.now()
        existing = models.Instance.objects.create(
            name='mastodon.social',
            up=True,
            https_score=81,
            https_rank="A",
            ipv6=False,
            open_registrations=True,
            users=330,
            statuses=1132540,
            last_fetched=now,
            connections=827,
            release=None,
        )

        data = existing.to_influxdb()
        expected = {
            'measurement': 'instances',
            'time': now.isoformat(),
            'fields': {
                '_quantity': 1,
                'https_score': 81,
                'users': 330,
                'statuses': 1132540,
                'connections': 827,
            },
            'tags': {
                'geohash': None,
                'name': 'mastodon.social',
                'ipv6': False,
                'https_rank': 'A',
                'up': True,
                'open_registrations': True,
                'country_code': None,
                'region_code': None,
                'region': None,
                'release_full': 'UNKNOWN',
                'release_major': 0,
                'release_minor': 0,
                'release_patch': 0,
            },
        }
        self.assertEqual(data, expected)

    @unittest.mock.patch('mnm.instances.influxdb_client.push')
    def test_can_send_data_to_influxdb(self, m):
        now = timezone.now()
        existing = InstanceFactory(
            name='mastodon.social',
            up=True,
            https_score=81,
            https_rank="A",
            ipv6=False,
            open_registrations=True,
            users=330,
            last_week_statuses=1,
            last_week_registrations=2,
            last_week_logins=3,
            country_code='FR',
            region_code='PA',
            region='Europe',
            statuses=1132540,
            last_fetched=now,
            connections=827
        )

        expected = {
            'measurement': 'instances',
            'time': now.isoformat(),
            'fields': {
                'https_score': 81,
                'users': 330,
                'statuses': 1132540,
                'connections': 827,
                '_quantity': 1,
                'last_week_statuses': 1,
                'last_week_registrations': 2,
                'last_week_logins': 3,
            },
            'tags': {
                'geohash': None,
                'country_code': 'FR',
                'region_code': 'PA',
                'region': 'Europe',
                'name': 'mastodon.social',
                'ipv6': False,
                'https_rank': 'A',
                'up': True,
                'open_registrations': True,
                'release_full': existing.release.version_string,
                'release_major': existing.release.tuple_version[0],
                'release_minor': existing.release.tuple_version[1],
                'release_patch': existing.release.tuple_version[2],
            },
        }

        existing.push_to_influxdb()

        m.assert_called_once_with([expected])

    @requests_mock.mock()
    def test_can_fetch_instance_country(self, m):
        html = os.path.join(DATA_DIR, 'freegeoip.json')
        with open(html) as f:
            content = f.read()

        hostname = 'mastodon.xyz'
        url = 'https://freegeoip.net/json/{}'.format(hostname)
        m.get(url, text=content)

        results = countries.fetch_country('mastodon.xyz')
        self.assertEqual(results['country_code'], 'FR')
        self.assertEqual(results['country_name'], 'France')
        self.assertEqual(results['time_zone'], 'Europe/Paris')
        self.assertEqual(results['latitude'], 48.8582)
        self.assertEqual(results['longitude'], 2.3387)

    def test_can_fetch_instance_country_from_tld(self):
        self.assertEqual(
            countries.fetch_country_from_tld('mastodon.fr'), 'FR')
        self.assertEqual(
            countries.fetch_country_from_tld('mastodon.es'), 'ES')
        self.assertEqual(
            countries.fetch_country_from_tld('mastodon.social'), None)

    @requests_mock.mock()
    def test_fetch_countries_uses_tld_countries_whenever_possible(self, m):
        existing = models.Instance.objects.create(
            name='mastodon.es',
        )
        # we mock by returning french IP, but the TLD is es, so it should be
        # spanish in the end
        html = os.path.join(DATA_DIR, 'freegeoip.json')
        with open(html) as f:
            content = f.read()

        hostname = 'mastodon.es'
        url = 'https://freegeoip.net/json/{}'.format(hostname)
        m.get(url, text=content)

        tasks.fetch_instances_countries()

        existing.refresh_from_db()

        self.assertEqual(existing.country_code, 'ES')
        self.assertEqual(existing.region, 'Europe')

    def test_can_get_instance_geohash(self):
        instance = models.Instance.objects.create(
            name='mastodon.social',
            latitude=40.6888,
            longitude=-74.0204,
        )

        self.assertEqual(instance.geohash, 'dr5')

    @requests_mock.mock()
    def test_can_fetch_instance_info(self, m):
        with self.settings(NOTIFY_ON_RELEASE=False):
            release = ReleaseFactory(tag='1.3')
        payload = """{"uri":"mastodon.social","title":"Mastodon","description":"","email":"eugen@zeonfederated.com","version":"1.3"}"""
        existing = models.Instance.objects.create(
            name='mastodon.social',
        )
        url = existing.get_info_api_url()
        self.assertEqual(url, 'https://mastodon.social/api/v1/instance')
        m.get(url, text=payload)

        tasks.fetch_instance_info(existing.pk)

        existing.refresh_from_db()

        self.assertEqual(existing.release, release)
        self.assertEqual(existing.release.version_major, 1)
        self.assertEqual(existing.release.version_minor, 3)
        self.assertEqual(existing.release.version_patch, 0)
