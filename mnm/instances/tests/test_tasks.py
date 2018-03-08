import pytest
import requests_mock

from . import factories
from .. import tasks


@pytest.fixture()
def m():
    with requests_mock.Mocker() as m:
        yield m


def test_fetch_instance_activity(db, m):
    instance = factories.InstanceFactory()
    url = instance.url + '/api/v1/instance/activity'
    m.get(url, json=[{'test': 'something'}])
    result = tasks._fetch_instance_activity(instance)
    assert result == [{'test': 'something'}]


def test_update_instance_activity(db, mocker):
    payload = {
        'statuses':	'6000',
        'logins': '38',
        'registrations': '11',
    }
    mocker.patch(
        'mnm.instances.tasks._fetch_instance_activity', return_value=[payload])
    instance = factories.InstanceFactory()
    tasks.update_instance_activity(instance.pk)
    instance.refresh_from_db()

    assert instance.last_week_statuses == 6000
    assert instance.last_week_logins == 38
    assert instance.last_week_registrations == 11
