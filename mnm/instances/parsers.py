import requests
import json
from django.utils import timezone
from django.conf import settings

from . import models


def parser_instances_social():
    url = 'https://instances.social/api/1.0/instances/list'
    headers = {'Authorization': 'Bearer {}'.format(settings.INSTANCES_SOCIAL_API_TOKEN)}
    response = requests.get(url, params={'count': 0}, headers=headers)
    response.raise_for_status()
    payload = json.loads(response.content.decode('utf-8'))
    now = timezone.now()
    results = {
        'instances': [],
        'fetched_on': now,
    }
    for row in payload['instances']:
        d = {
            'name': row['name'].lower(),
            'up': row['up'],
            'https_score': row['https_score'],
            'https_rank': row['https_rank'],
            'ipv6': row['ipv6'],
            'open_registrations': row['open_registrations'],
            'users': row['users'],
            'statuses': row['statuses'],
            'connections': row['connections'],
            'fetched_on': now,
        }
        results['instances'].append(d)
    return results


def import_results(results):
    instances = []
    for row in results:
        row['last_fetched'] = row.pop('fetched_on')
        try:
            i, _ = models.Instance.objects.select_related().update_or_create(
                name=row['name'],
                defaults=row,
            )
        except Exception as e:
            print('ERROR while importing result:', row, e)
            continue
        instances.append(i)

    return instances
