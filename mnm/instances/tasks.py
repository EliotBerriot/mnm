from django.utils import timezone
import itertools

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


def fetch_instances():
    results = parsers.parser_instances_xyz()
    parsers.import_results(results['instances'])

    data = []
    for instance in models.Instance.objects.all():
        data.append(instance.to_influxdb())
    for group in grouper(50, data):
        influxdb_client.push(list(group))
