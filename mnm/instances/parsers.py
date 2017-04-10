import requests
import json
from django.utils import timezone

from . import models


def parser_instances_xyz():
    url = 'https://instances.mastodon.xyz/instances.json'
    response = requests.get(url)
    response.raise_for_status()
    payload = json.loads(response.content.decode('utf-8'))
    now = timezone.now()
    results = {
        'instances': [],
        'fetched_on': now,
    }
    for row in payload:
        try:
            d = {
                'name': row['name'],
                'up': row['up'],
                'https_score': row['https_score'],
                'https_rank': row['https_rank'],
                'ipv6': row['ipv6'],
                'open_registrations': row.get('openRegistrations'),
                'users': row.get('users'),
                'statuses': row.get('statuses'),
                'connections': row.get('connections'),
                'fetched_on': now,
            }
        except Exception as e:
            print('ERROR while parsing result:', e)
            continue
        results['instances'].append(d)
    return results


def import_results(results):
    instances = []
    for row in results:
        row['last_fetched'] = row.pop('fetched_on')
        try:
            i, _ = models.Instance.objects.update_or_create(
                name=row['name'],
                defaults=row,
            )
        except Exception as e:
            print('ERROR while importing result:', row)
            continue
        instances.append(i)

    return instances
