import factory
from django.utils import timezone

from mnm.releases.tests.factories import ReleaseFactory


class InstanceFactory(factory.django.DjangoModelFactory):

    name = factory.Faker('domain_name')
    release = factory.SubFactory(ReleaseFactory)

    class Meta:
        model = 'instances.Instance'
