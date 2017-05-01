import factory
from django.utils import timezone


class ReleaseFactory(factory.django.DjangoModelFactory):

    tag = '1.3.1'
    url = factory.Faker('url')
    body = factory.Faker('paragraph')
    creation_date = factory.LazyFunction(timezone.now)
    release_date = factory.SelfAttribute('creation_date')

    class Meta:
        model = 'releases.Release'
