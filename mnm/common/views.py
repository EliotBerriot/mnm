
from django.views import generic
from django.conf import settings

from mnm.instances.models import Instance


class Index(generic.TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['biggest_instances'] = Instance.objects.public().order_by('-users')[:10]
        return context
