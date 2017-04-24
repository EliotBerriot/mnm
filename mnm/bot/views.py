from django.views import generic
from django.conf import settings

from . import commands


class HelpView(generic.TemplateView):
    template_name = 'bot/help.html'

    def get_context_data(self):
        context = super().get_context_data()

        context['commands'] = [
            c for c in commands.commands.values()
            if c.show_in_help
        ]
        context['bot_name'] = settings.STATS_BOT['name']
        return context
