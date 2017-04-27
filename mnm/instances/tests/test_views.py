import unittest
from test_plus.test import TestCase
from mnm.instances import models


class TestViews(TestCase):

    def test_can_create_instance(self):
        i1 = models.Instance.objects.create(
            name='test1.io',
            users=100,
        )
        i2 = models.Instance.objects.create(
            name='test2.io',
            users=102,
        )

        url = self.reverse('instances:index')
        response = self.client.get(url)
        expected = models.Instance.objects.public().order_by('-users')

        self.assertEqual(list(response.context['instances']), list(expected))
