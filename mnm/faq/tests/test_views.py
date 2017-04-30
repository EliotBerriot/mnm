import unittest
from test_plus.test import TestCase
from mnm.faq import models
from django.utils import timezone

from . import factories


class TestViews(TestCase):

    def test_can_list_FAQ(self):
        e1 = factories.Entry(status='published', sort_order=2)
        e2 = factories.Entry(status='draft')
        e3 = factories.Entry(status='published', sort_order=1)

        url = self.reverse('faq:index')
        response = self.client.get(url)
        expected = [e3, e1]

        self.assertEqual(list(response.context['entries']), list(expected))
