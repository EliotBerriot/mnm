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
