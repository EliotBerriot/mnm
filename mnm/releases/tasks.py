from mnm.taskapp import celery

from . import parsers


@celery.app.task(bind=True)
def fetch_and_import_releases(self):
    data = parsers.fetch_releases()
    releases = parsers.import_releases(data)
    return len(releases)
