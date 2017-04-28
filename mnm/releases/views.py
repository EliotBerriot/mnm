from django.views import generic
from django.conf import settings

from . import models


class ReleasesIndex(generic.ListView):
    template_name = 'releases/index.html'
    queryset = models.Release.objects.all()
    context_object_name = 'releases'
