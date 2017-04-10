import influxdb
from django.conf import settings


_client = None


def get_client():
    global _client
    if not _client:
        _client = influxdb.InfluxDBClient.from_DSN(
            settings.INFLUXDB_URL,
            udp_port=settings.INFLUXDB_UDP_PORT,
            timeout=5)
    return _client


def push(data):
    client = get_client()
    return client.write_points(data)
