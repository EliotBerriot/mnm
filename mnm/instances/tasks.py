from . import parsers


def fetch_instances():
    results = parsers.parser_instances_xyz()
    parsers.import_results(results['instances'])
