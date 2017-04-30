import factory


class Entry(factory.django.DjangoModelFactory):

    title = factory.Faker('sentence')
    content = factory.Faker('paragraph')

    class Meta:
        model = 'faq.Entry'
