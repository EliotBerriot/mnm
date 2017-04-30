from django.views import generic
from django.conf import settings

from . import models


class FAQIndex(generic.ListView):
    template_name = 'faq/index.html'
    queryset = models.Entry.objects.public()
    context_object_name = 'entries'
