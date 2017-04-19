from mnm.taskapp import celery
from django.utils.html import strip_tags
from mnm.instances import influxdb_client
from mnm.instances.models import Instance


@celery.app.task(bind=True)
def send_to_influxdb(self, data):
    p = {
        'measurement': 'statuses',
        'time': data['created_at'],
        'fields': {
            '_quantity': 1,
        },
        'tags': {

        }
    }
    p['fields']['mentions_count'] = len(data['mentions'])
    p['fields']['tags_count'] = len(data['tags'])
    p['fields']['tags'] = ','.join(
        sorted([t['name'].lower() for t in data['tags']])
    )
    p['fields']['media_count'] = len(data['media_attachments'])
    p['fields']['images_count'] = len(
        [a for a in data['media_attachments'] if a['type'] == 'image'])
    p['fields']['links_count'] = data['content'].count('<a href=')
    p['fields']['content_length'] = len(strip_tags(data['content']))
    p['tags']['is_reply'] = data['in_reply_to_account_id'] is not None
    p['tags']['is_reblog'] = data['reblog'] is not None
    p['tags']['is_sensitive'] = data['sensitive']

    instance = data['uri'].split(',')[0].split(':')[1]
    p['tags']['instance'] = instance
    try:
        instance = Instance.objects.get(name=p['tags']['instance'])
        p['tags']['instance_country_code'] = instance.country_code
    except Instance.DoesNotExist:
        pass
    p['tags']['application'] = data['application'] or 'web'
    p['tags']['visibility'] = data['visibility']
    p['tags']['has_images'] = p['fields']['images_count'] > 0
    p['tags']['has_links'] = p['fields']['links_count'] > 0

    points = [p]

    for t in p['fields']['tags'].split(','):
        d = {
            'measurement': 'hashtags',
            'time': data['created_at'],
            'fields': {
                '_quantity': 1,
            },
            'tags': {
                'name': t,
                'instance_country_code': p['tags'].get('instance_country_code')
            }
        }
        points.append(d)

    influxdb_client.push(points)

    return p
