import os
import requests
import requests_mock
from test_plus.test import TestCase
from mnm.instances import models, parsers

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class TestInstances(TestCase):

    def test_can_create_instance(self):
        instance = models.Instance.objects.create(
            url='https://test.io',
        )

        self.assertIsNone(instance.last_fetched)
        self.assertIsNone(instance.users)
        self.assertIsNone(instance.statuses)
        self.assertIsNone(instance.connections)
        self.assertIsNone(instance.open_registration)
        self.assertIsNone(instance.up)

    @requests_mock.mock()
    def test_can_extract_instances_list_from_instances_xyz(self, m):
        html = os.path.join(DATA_DIR, 'instances.mastodon.xyz.html')
        with open(html) as f:
            content = f.read()

        m.get('https://instances.mastodon.xyz', text=content)
        results = parsers.parser_instances_xyz()

        self.assertEqual(len(results['instances']), 3)
        self.assertEqual(results['instances'][0]['url'], 'https://hex.bz')
        self.assertEqual(results['instances'][0]['users'], 330)
        self.assertEqual(results['instances'][0]['open_registration'], True)
        self.assertEqual(results['instances'][0]['up'], True)

        self.assertEqual(results['instances'][1]['url'], 'https://mastodon.opportunis.me')
        self.assertEqual(results['instances'][1]['users'], 1)
        self.assertEqual(results['instances'][1]['open_registration'], False)
        self.assertEqual(results['instances'][1]['up'], False)

        self.assertEqual(results['instances'][2]['url'], 'https://soc.mtb.wtf')
        self.assertEqual(results['instances'][2]['users'], 13)
        self.assertEqual(results['instances'][2]['open_registration'], True)
        self.assertEqual(results['instances'][2]['up'], True)

    @requests_mock.mock()
    def test_can_get_or_create_instances_based_on_parse_results(self, m):
        existing = models.Instance.objects.create(
            url='https://hex.bz',
        )
        html = os.path.join(DATA_DIR, 'instances.mastodon.xyz.html')
        with open(html) as f:
            content = f.read()

        m.get('https://instances.mastodon.xyz', text=content)
        results = parsers.parser_instances_xyz()

        instances = parsers.import_results(results['instances'])

        expected = [
            {
                'url': 'https://hex.bz',
                'users': 330,
                'open_registration': True,
                'up': True,
            },
            {
                'url': 'https://mastodon.opportunis.me',
                'users': 1,
                'open_registration': False,
                'up': False,
            },
            {
                'url': 'https://soc.mtb.wtf',
                'users': 13,
                'open_registration': True,
                'up': True,
            },
        ]

        self.assertEqual(existing, instances[0])

        for i, instance in enumerate(instances):
            for key, value in expected[i].items():
                self.assertEqual(getattr(instance, key), value)

        # we can rerun the same method without duplicating instances
        instances = parsers.import_results(results['instances'])
        self.assertEqual(models.Instance.objects.count(), 3)
        for i, instance in enumerate(instances):
            for key, value in expected[i].items():
                self.assertEqual(getattr(instance, key), value)
    @requests_mock.mock()
    def test_can_fetch_instance_data_from_about_page(self, m):
        html = os.path.join(DATA_DIR, 'instance.about.html')
        with open(html) as f:
            content = f.read()

        url = 'https://instance.com'
        m.get(url, text=content)
        results = parsers.fetch_instance_data(url)

        self.assertEqual(results['users'], 123)
        self.assertEqual(results['statuses'], 207)
        self.assertEqual(results['connections'], 16)
