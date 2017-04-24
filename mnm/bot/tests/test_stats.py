import unittest
from test_plus.test import TestCase
from influxdb.resultset import ResultSet

from mnm.bot import stats

import requests_mock


class TestStats(TestCase):
    """
    to get the mock output, just run
    curl -G 'http://localhost:8086/query' --data-urlencode 'db=mnm' --data-urlencode 'q=INFLUXDB QUERY'

    on your influxdb server

    """

    def test_users_stat(self):
        c = stats.stats['users']

        payload = """
        {
            "results": [
                {
                    "statement_id": 0,
                    "series": [
                        {
                            "name": "instances_hourly",
                            "columns": [
                                "time",
                                "sum"
                            ],
                            "values": [
                                [
                                    "2017-04-23T19:00:00Z",
                                    10
                                ],
                                [
                                    "2017-04-23T20:00:00Z",
                                    12
                                ],
                                [
                                    "2017-04-24T18:00:00Z",
                                    17
                                ],
                                [
                                    "2017-04-24T19:00:00Z",
                                    20
                                ]
                            ]
                        }
                    ]
                }
            ]
        }"""
        with requests_mock.Mocker() as m:
            m.register_uri(
                requests_mock.GET,
                "http://influxdb:8086/query",
                text=payload)
            response = c.get()

        self.assertEqual(response['24h'], 10)
        self.assertEqual(response['1h'], 3)
        self.assertEqual(response['total'], 20)
