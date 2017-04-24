import unittest
from test_plus.test import TestCase
from django.core.urlresolvers import reverse
from mnm.bot import bot, commands


class TestBot(TestCase):

    def test_bot_can_send_toot(self):
        b = bot.Bot()

        with unittest.mock.patch('mastodon.Mastodon.status_post') as m:
            b.publish('Hello world', visibility='public')

            m.assert_called_once_with(
                'Hello world', visibility='public', in_reply_to_id=None)

    def test_bot_can_parse_command(self):
        b = bot.Bot()

        command, arguments = b.parse('@bot /help')

        self.assertEqual(command, 'help')
        self.assertEqual(arguments, [])

    def test_bot_parse_only_slash_commands(self):
        b = bot.Bot()

        command, arguments = b.parse('@bot nope')

        self.assertEqual(command, None)
        self.assertEqual(arguments, [])

    def test_empty_message_means_help(self):
        b = bot.Bot()

        command, arguments = b.parse('@bot')

        self.assertEqual(command, 'help')
        self.assertEqual(arguments, [])

    def test_can_receive_toot_and_get_reply(self):
        b = bot.Bot()

        status = {
            'account': {
                'acct': 'test@instance',
                'created_at': '2017-04-22T15:47:24.057Z',
                'display_name': 'Test user',
                'id': 1,
                'locked': False,
                'statuses_count': 3,
                'url': 'https://instance/@test',
                'username': 'test',
                },
            'application': {'name': 'mnm', 'website': None},
            'content': '<p><span class="h-card"><a href="https://mastodon.test/@mnm" class="u-url mention">@<span>mnm</span></a></span> /help</p>',
            'created_at': '2017-04-24T20:06:42.910Z',
            'favourited': False,
            'favourites_count': 0,
            'id': 1,
            'in_reply_to_account_id': None,
            'in_reply_to_id': None,
            'media_attachments': [],
            'mentions': [{
                'acct': 'mnm',
                'id': 1,
                'url': 'https://mastodon.test/@mnm',
                'username': 'mnm',
                }],
            'reblog': None,
            'reblogged': False,
            'reblogs_count': 0,
            'sensitive': None,
            'spoiler_text': '',
            'tags': [],
            'uri': 'instance,2017-04-24:objectId=1:objectType=Status',
            'url': 'https://instance/@test/1',
            'visibility': 'direct',
        }

        reply = b.get_response(status)

        self.assertIn(reverse('bot:help'), reply['status'])
        self.assertIn('@test@instance', reply['status'])
        self.assertEqual('direct', reply['visibility'])
        self.assertEqual(reply['in_reply_to_id'], 1)

    def test_can_receive_toot_and_get_reply(self):
        b = bot.Bot()

        status = {
            'account': {
                'acct': 'test@instance',
                'id': 1,
                'url': 'https://instance/@test',
                'username': 'test',
                },
            'content': '<p><span class="h-card"><a href="https://mastodon.test/@mnm" class="u-url mention">@<span>mnm</span></a></span> /help</p>',
            'id': 1,
            'in_reply_to_account_id': None,
            'in_reply_to_id': None,
            'mentions': [{
                'acct': 'mnm',
                'id': 1,
                'url': 'https://mastodon.test/@mnm',
                'username': 'mnm',
                }],
            'sensitive': None,
            'spoiler_text': '',
            'tags': [],
            'uri': 'instance,2017-04-24:objectId=1:objectType=Status',
            'url': 'https://instance/@test/1',
            'visibility': 'direct',
        }

        with unittest.mock.patch('mnm.bot.bot.Bot.publish') as m:
            reply, api_response = b.handle(status)

        self.assertIn(reverse('bot:help'), reply['status'])
        self.assertIn('@test@instance', reply['status'])
        self.assertEqual('direct', reply['visibility'])
        self.assertEqual(reply['in_reply_to_id'], 1)

    def test_can_handle_unknown_command(self):
        b = bot.Bot()

        status = {
            'account': {
                'acct': 'test@instance',
                'id': 1,
                'url': 'https://instance/@test',
                'username': 'test',
                },
            'content': '<p><span class="h-card"><a href="https://mastodon.test/@mnm" class="u-url mention">@<span>mnm</span></a></span> /nopesorry</p>',
            'id': 1,
            'in_reply_to_account_id': None,
            'in_reply_to_id': None,
            'mentions': [{
                'acct': 'mnm',
                'id': 1,
                'url': 'https://mastodon.test/@mnm',
                'username': 'mnm',
                }],
            'sensitive': None,
            'spoiler_text': '',
            'tags': [],
            'uri': 'instance,2017-04-24:objectId=1:objectType=Status',
            'url': 'https://instance/@test/1',
            'visibility': 'direct',
        }

        reply = b.get_response(status)

        self.assertIn('/help', reply['status'])
        self.assertIn('@test@instance', reply['status'])
        self.assertEqual('direct', reply['visibility'])
        self.assertEqual(reply['in_reply_to_id'], 1)

    def test_do_not_react_if_no_slash_command(self):
        b = bot.Bot()

        status = {
            'account': {
                'acct': 'test@instance',
                'id': 1,
                'url': 'https://instance/@test',
                'username': 'test',
                },
            'content': '<p><span class="h-card"><a href="https://mastodon.test/@mnm" class="u-url mention">@<span>mnm</span></a></span> hello there!</p>',
            'id': 1,
            'in_reply_to_account_id': None,
            'in_reply_to_id': None,
            'mentions': [{
                'acct': 'mnm',
                'id': 1,
                'url': 'https://mastodon.test/@mnm',
                'username': 'mnm',
                }],
            'sensitive': None,
            'spoiler_text': '',
            'tags': [],
            'uri': 'instance,2017-04-24:objectId=1:objectType=Status',
            'url': 'https://instance/@test/1',
            'visibility': 'direct',
        }

        reply = b.get_response(status)

        self.assertEqual(reply, None)

    def test_error_handling(self):
        b = bot.Bot()

        status = {
            'account': {
                'acct': 'test@instance',
                'id': 1,
                'url': 'https://instance/@test',
                'username': 'test',
                },
            'content': '<p><span class="h-card"><a href="https://mastodon.test/@mnm" class="u-url mention">@<span>mnm</span></a></span> /stats users</p>',
            'id': 1,
            'in_reply_to_account_id': None,
            'in_reply_to_id': None,
            'mentions': [{
                'acct': 'mnm',
                'id': 1,
                'url': 'https://mastodon.test/@mnm',
                'username': 'mnm',
                }],
            'sensitive': None,
            'spoiler_text': '',
            'tags': [],
            'uri': 'instance,2017-04-24:objectId=1:objectType=Status',
            'url': 'https://instance/@test/1',
            'visibility': 'direct',
        }

        with unittest.mock.patch('mnm.bot.stats.UsersStat.get', side_effect=Exception):
            reply = b.get_response(status)

        self.assertIn('error', reply['status'])
        self.assertIn('https://github.com/EliotBerriot/mnm/issues', reply['status'])
