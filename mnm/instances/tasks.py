from django.utils import timezone
import itertools
import requests
from mnm.taskapp import celery

from . import parsers
from . import models
from . import influxdb_client


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
    for instance in models.Instance.objects.all():
        data.append(instance.to_influxdb(table=table))
    for group in grouper(50, data):
        influxdb_client.push(list(group))


@celery.app.task(bind=True)
def fetch_instances_countries(self, maximum=10, empty=True):
    qs = models.Instance.objects.filter(country_code__isnull=empty)

    for instance in qs.order_by('?')[:maximum]:
        print('Fetching geo data for {}...'.format(instance.name))
        try:
            data = parsers.fetch_country(instance.name)
        except requests.HTTPError:
            continue

        instance.import_geoip_data(data)
        instance.save()
