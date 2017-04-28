import requests
import datetime

from . import models

RELEASES_URL = 'https://api.github.com/repos/tootsuite/mastodon/releases'


def fetch_releases():
    date_format = '%Y-%m-%dT%H:%M:%SZ'
    response = requests.get(RELEASES_URL)
    response.raise_for_status()

    releases = response.json()
    final_releases = []
    for r in releases:
        if r['draft'] or r['prerelease']:
            continue
        r['created_at'] = datetime.datetime.strptime(
            r['created_at'], date_format)
        r['published_at'] = datetime.datetime.strptime(
            r['published_at'], date_format)

        final_releases.append(r)
    return final_releases


def import_releases(data):
    releases = []
    for row in data:
        data = {
            'creation_date': row['created_at'],
            'release_date': row['published_at'],
            'body': row['body'],
            'url': row['html_url'],
        }
        i, _ = models.Release.objects.update_or_create(
            tag=row['tag_name'],
            defaults=data,
        )
        releases.append(i)

    return releases
