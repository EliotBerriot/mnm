import unittest
from test_plus.test import TestCase

from mnm.bot import bot, commands


class TestBot(TestCase):

    def test_bot_can_send_toot(self):
        b = bot.Bot()

        with unittest.mock.patch('mastodon.Mastodon.status_post') as m:
            b.publish('Hello world', visibility='public')

            m.assert_called_once_with('Hello world', visibility='public')

    def test_bot_can_parse_command(self):
        b = bot.Bot()

        command, arguments = b.parse('@bot /help')

        self.assertEqual(command, 'help')
        self.assertEqual(arguments, [])

    def test_bot_parse_only_slash_commands(self):
        b = bot.Bot()

        command, arguments = b.parse('@bot nope')

        self.assertEqual(command, None)
        self.assertEqual(arguments, None)

    def test_empty_message_means_no_command(self):
        b = bot.Bot()

        command, arguments = b.parse('@bot')

        self.assertEqual(command, None)
        self.assertEqual(arguments, None)
