from django.utils import timezone
import itertools
import requests
from mnm.taskapp import celery
from celery.utils.log import get_task_logger

from mnm.releases.models import Release

from . import parsers
from . import countries
from . import models
from . import influxdb_client

logger = get_task_logger(__name__)


def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it)


@celery.app.task(bind=True)
def fetch_instances(self, table):
    results = parsers.parser_instances_xyz()
    parsers.import_results(results['instances'])

    data = []
    for instance in models.Instance.objects.filter(is_blocked=False):
        data.append(instance.to_influxdb(table=table))
    for group in grouper(50, data):
        influxdb_client.push(list(group))


def fetch_host_geo_data(hostname):
    geoip_data = countries.fetch_country(hostname)
    tld_country = countries.fetch_country_from_tld(hostname)
    country = tld_country or geoip_data['country_code']
    region = countries.get_country_region(country)

    return {
        'country': country,
        'region': region,
        'geoip_data': geoip_data
    }


@celery.app.task(bind=True)
def fetch_instances_countries(self, maximum=10, empty=True):
    qs = models.Instance.objects.filter(country_code__isnull=empty)

    for instance in qs.order_by('?')[:maximum]:
        logger.info('Fetching geo data for {}...'.format(instance.name))
        try:
            data = fetch_host_geo_data(instance.name)
        except requests.HTTPError:
            continue

        instance.latitude = data['geoip_data']['latitude']
        instance.longitude = data['geoip_data']['longitude']
        instance.country_code = data['country']
        instance.region = data['region']
        instance.save()


@celery.app.task(bind=True)
def fetch_instances_info(maximum=30):
    for instance in models.Instance.objects.all().order_by('?')[:maximum]:
        fetch_instance_info.delay(instance.pk)


@celery.app.task(bind=True)
def fetch_instance_info(self, instance_pk):
    instance = models.Instance.objects.get(pk=instance_pk)
    response = requests.get(instance.get_info_api_url())
    response.raise_for_status()
    payload = response.json()
    try:
        version_string = payload['version']
        release = Release.objects.get_from_version_string(version_string)
        instance.release = release
        instance.save()
    except (Release.DoesNotExist, KeyError, IndexError):
        pass

    return payload
