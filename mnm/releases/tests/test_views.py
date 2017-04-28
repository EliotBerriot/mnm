import unittest
from test_plus.test import TestCase
from mnm.releases import models
from django.utils import timezone


class TestViews(TestCase):

    def test_can_list_releases(self):
        i1 = models.Release.objects.create(
            tag='1.2',
            url='http://test.release1',
            release_date=timezone.now(),
        )
        i2 = models.Release.objects.create(
            tag='1.3',
            url='http://test.release2',
            release_date=timezone.now(),
        )

        url = self.reverse('releases:index')
        response = self.client.get(url)
        expected = [i2, i1]

        self.assertEqual(list(response.context['releases']), list(expected))
