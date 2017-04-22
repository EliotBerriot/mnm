import os
import json
import requests
import functools


def fetch_country(hostname):
    """
    For a given hostname or IP, make a request to freegeoip and return the
    results
    """

    url = 'https://freegeoip.net/json/{}'.format(hostname)
    response = requests.get(url)
    response.raise_for_status()
    payload = json.loads(response.content.decode('utf-8'))
    return payload


@functools.lru_cache(maxsize=1)
def get_countries_data():
    countries_file = os.path.join(
        os.path.dirname(__file__), 'countries.json')
    with open(countries_file) as f:
        return json.load(f)


def fetch_country_from_tld(hostname):

    tld = '.{}'.format(hostname.split('.')[-1])
    candidates = [
        c['cca2']
        for c in get_countries_data()
        if tld in c.get('tld')
    ]
    try:
        return candidates[0]
    except IndexError:
        return None


def get_country_region(country):
    candidates = [
        c['region']
        for c in get_countries_data()
        if country == c['cca2']
    ]
    try:
        return candidates[0]
    except IndexError:
        return None
