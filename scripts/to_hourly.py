from mnm.instances.influxdb_client import get_client
import datetime
from django.utils import timezone

interval = 3600
existing_interval = 300
client = get_client()
new_table = 'instances_hourly'

start = timezone.now().replace(minute=0, second=0, microsecond=0)
current = start
while True:
    query = """
    SELECT * FROM instances WHERE time > '{}' AND time < '{}';""".format(
        (current - datetime.timedelta(seconds=existing_interval)).isoformat(),
        current.isoformat(),
    )
    results = client.query(query).get_points('instances')
    new_points = []
    for r in results:
        n = {
            "measurement": new_table,
            "time": r['time'],
            "tags": {
                'open_registrations': r['open_registrations'],
                'up': r['up'],
                'https_rank': r['https_rank'],
                'ipv6': r['ipv6'],
                'name': r['name'],
                'country_code': r['country_code'],
                'region_code': r['region_code'],
                'geohash': r['geohash'],
            },
            "fields": {
                '_quantity': r['_quantity'],
                'https_score': r['https_score'],
                'statuses': r['statuses'],
                'users': r['users'],
                'connections': r['connections'],
            },
        }
        new_points.append(n)
    print(len(new_points), query)
    print(new_points[:1])
    client.write_points(new_points)
    current = current - datetime.timedelta(seconds=interval)
