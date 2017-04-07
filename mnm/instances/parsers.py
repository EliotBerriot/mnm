import lxml.html
import requests

from . import models


def parser_instances_xyz():
    url = 'https://instances.mastodon.xyz'
    response = requests.get(url)
    response.raise_for_status()
    root = lxml.html.fromstring(response.content.decode('utf-8'))
    rows = root.xpath('//tbody/tr')
    results = {
        'instances': []
    }
    for row in rows:
        d = {}
        cells = row.xpath('td')
        up, url, users, registrations = (
            cells[0],
            cells[1],
            cells[2],
            cells[3],
        )
        d['up'] = up.text.lower() == 'up'
        d['url'] = url.findall('.//a')[0].attrib['href']
        d['users'] = int(users.text)
        d['open_registration'] = registrations.text.lower() == 'yes'
        results['instances'].append(d)

    return results


def import_results(results):
    instances = []
    for row in results:
        i, _ = models.Instance.objects.update_or_create(
            url=row['url'],
            defaults=row,
        )
        instances.append(i)

    return instances


def fetch_instance_data(url):
    response = requests.get(url)
    response.raise_for_status()

    root = lxml.html.fromstring(response.content.decode('utf-8'))
    informations = root.xpath("//div[@class='information-board']/div/strong")
    users, statuses, connections = (
        informations[0],
        informations[1],
        informations[2],
    )
    results = {
        'users': int(users.text),
        'statuses': int(statuses.text),
        'connections': int(connections.text),
    }

    return results
