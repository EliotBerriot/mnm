from test_plus.test import TestCase

from . import factories
from mnm.faq import models


class TestModels(TestCase):

    def test_faq_entry(self):
        e = factories.Entry(content='hello', title='world')

        self.assertEqual(e.content_rendered, '<p>hello</p>')
        self.assertEqual(e.sort_order, 0)
        self.assertEqual(e.status, 'draft')

    def test_public_queryset_excludes_drafts(self):
        e1 = factories.Entry(status='draft')
        e2 = factories.Entry(status='published')

        self.assertEqual(list(models.Entry.objects.public()), [e2])
