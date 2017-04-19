import unittest
from test_plus.test import TestCase
from django.utils.html import strip_tags
from mnm.statuses import tasks

from mnm.instances.models import Instance


class TestStatus(TestCase):

    def test_can_send_to_influxdb(self):
        instance = Instance.objects.create(
            name='oc.todon.fr',
            country_code='FR',
        )
        data = {
            'application': None,
            'media_attachments': [
                {'id': 67449,
                'text_url': None,
                'url': 'https://mastodon.xyz/system/media_attachments/files/000/067/449/original/fd4db85fe742f73c.jpg?1492542253',
                'preview_url': 'https://mastodon.xyz/system/media_attachments/files/000/067/449/small/fd4db85fe742f73c.jpg?1492542253',
                'type': 'image',
                'remote_url': 'https://oc.todon.fr/system/media_attachments/files/000/025/877/original/fd4db85fe742f73c.jpg'}],
            'id': 1009662,
            'in_reply_to_account_id': None,
            'visibility': 'public',
            'favourites_count': 0,
            'mentions': [],
            'account': {
                'locked': False,
                'avatar': 'https://mastodon.xyz/system/accounts/avatars/000/015/761/original/d76e06ea03e46978.jpg?1491674870',
                'id': 15761,
                'following_count': 1,
                'avatar_static': 'https://mastodon.xyz/system/accounts/avatars/000/015/761/original/d76e06ea03e46978.jpg?1491674870',
                'header_static': 'https://mastodon.xyz/system/accounts/headers/000/015/761/original/6cda3f9ad6aa25a6.jpg?1491674870',
                'followers_count': 16,
                'display_name': 'Freya Lunacy',
                'created_at': '2017-04-06T08:49:46.249Z',
                'acct': 'Freyalunacy@oc.todon.fr',
                'url': 'https://oc.todon.fr/@Freyalunacy',
                'note': 'Angelic Black ~ Legs and Lace ~ Moon and Crystal ~ Little Doll ~ Spongebob Squarepant ~ Cultural Studies',
                'statuses_count': 491,
                'header': 'https://mastodon.xyz/system/accounts/headers/000/015/761/original/6cda3f9ad6aa25a6.jpg?1491674870',
                'username': 'Freyalunacy'
            },
            'sensitive': True,
            'reblog': None,
            'reblogs_count': 0,
            'in_reply_to_id': None,
            'url': 'https://oc.todon.fr/users/Freyalunacy/updates/23999',
            'tags': [
                {'name': 'mastochef', 'url': 'https://mastodon.xyz/tags/mastochef'},
                {'name': 'Test', 'url': 'https://mastodon.xyz/tags/test'},
                {'name': 'photo', 'url': 'https://mastodon.xyz/tags/photo'},
            ],
            'created_at': '2017-04-18T19:04:12.000Z',
            'content': '<p>Partage photo du soir : Un joli portrait en noir et blanc ~ <br>Photographe : Dominique Weisrock</p><p><a href="https://oc.todon.fr/media/8WuCAB17ozgIB6BX6vU" rel="nofollow noopener"><span class="invisible">https://</span><span class="ellipsis">oc.todon.fr/media/8WuCAB17ozgI</span><span class="invisible">B6BX6vU</span></a></p>',
            'uri': 'tag:oc.todon.fr,2017-04-18:objectId=424018:objectType=Status', 'spoiler_text': ''}

        expected = {
            'measurement': 'statuses',
            'time': '2017-04-18T19:04:12.000Z',
            'fields': {
                '_quantity': 1,
                'mentions_count': 0,
                'tags_count': 3,
                'tags': 'mastochef,photo,test',
                'media_count': 1,
                'images_count': 1,
                'links_count': 1,
                'content_length': len(strip_tags(data['content']))
            },
            'tags': {
                'is_reply': False,
                'is_reblog': False,
                'is_sensitive': True,
                'instance': "oc.todon.fr",
                'instance_country_code': "FR",
                'application': "web",
                'visibility': "public",
                'has_images': True,
                'has_links': True,
            }
        }
        with unittest.mock.patch('mnm.instances.influxdb_client.push') as m:
            r = tasks.send_to_influxdb(data)
            m.assert_called_once_with([expected])
