import os
import unittest
import requests
import requests_mock
from test_plus.test import TestCase
from mnm.instances import models, parsers
from django.utils import timezone

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

        m.get('https://instances.mastodon.xyz/instances.json', text=content)
        results = parsers.parser_instances_xyz()

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
        m.get('https://instances.mastodon.xyz/instances.json', text=content)
        with unittest.mock.patch('django.utils.timezone.now', return_value=now):
            results = parsers.parser_instances_xyz()

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
            results = parsers.parser_instances_xyz()
        instances = parsers.import_results(results['instances'])
        self.assertEqual(models.Instance.objects.count(), 2)
        for i, instance in enumerate(instances):
            for key, value in expected[i].items():
                self.assertEqual(getattr(instance, key), value)

    def test_can_serialize_instnce_to_influxdb(self):
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
            connections=827
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
            },
        }
        self.assertEqual(data, expected)

    @unittest.mock.patch('mnm.instances.influxdb_client.push')
    def test_can_send_data_to_influxdb(self, m):
        now = timezone.now()
        existing = models.Instance.objects.create(
            name='mastodon.social',
            up=True,
            https_score=81,
            https_rank="A",
            ipv6=False,
            open_registrations=True,
            users=330,
            country_code='FR',
            region_code='PA',
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
            },
            'tags': {
                'geohash': None,
                'country_code': 'FR',
                'region_code': 'PA',
                'name': 'mastodon.social',
                'ipv6': False,
                'https_rank': 'A',
                'up': True,
                'open_registrations': True,
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

        results = parsers.fetch_country('mastodon.xyz')
        self.assertEqual(results['country_code'], 'FR')
        self.assertEqual(results['country_name'], 'France')
        self.assertEqual(results['time_zone'], 'Europe/Paris')
        self.assertEqual(results['latitude'], 48.8582)
        self.assertEqual(results['longitude'], 2.3387)

    def test_can_get_instance_geohash(self):
        instance = models.Instance.objects.create(
            name='mastodon.social',
            latitude=40.6888,
            longitude=-74.0204,
        )

        self.assertEqual(instance.geohash, 'dr5r7')
