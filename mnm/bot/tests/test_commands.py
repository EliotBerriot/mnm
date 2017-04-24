import unittest
from test_plus.test import TestCase
from django.core.urlresolvers import reverse
from mnm.bot import bot, commands


class TestCommands(TestCase):

    def test_help_command(self):
        c = commands.commands['help']
        response = c.handle(
            sender='me@test',
        )

        self.assertIn(reverse('bot:help'), response)

    def test_stat_user_command(self):
        c = commands.commands['stats']

        expected = {
            'total': 1789,
            '1h': 12,
            '24h': 1208,
        }
        with unittest.mock.patch('mnm.bot.stats.UsersStat.get', return_value=expected):
            response = c.handle(
                'me@test',
                *['users'],
            )

        self.assertIn('1789', response)
        self.assertIn('12', response)
        self.assertIn('1208', response)
