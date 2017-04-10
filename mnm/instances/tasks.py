from django.utils import timezone

from . import parsers
from . import models
from . import influxdb_client


def fetch_instances():
    results = parsers.parser_instances_xyz()
    parsers.import_results(results['instances'])

    data = []
    for instance in models.Instance.objects.all():
        data.append(instance.to_influxdb())
    for row in data:
        influxdb_client.push([row])
