import unittest
from test_plus.test import TestCase

from mnm.bot import bot


class TestBot(TestCase):

    def test_bot_can_send_toot(self):
        b = bot.Bot()

        with unittest.mock.patch('mastodon.Mastodon.status_post') as m:
            b.publish('Hello world', visibility='public')

            m.assert_called_once_with('Hello world', visibility='public')
