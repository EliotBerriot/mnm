from django.views import generic
from django.conf import settings

from . import models


class InstancesIndex(generic.ListView):
    template_name = 'instances/index.html'
    queryset = models.Instance.objects.public().order_by('-users')
    context_object_name = 'instances'
    paginate_by = 25
