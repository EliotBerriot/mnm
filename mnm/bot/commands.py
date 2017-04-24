import collections
from django.template import loader, Context, TemplateDoesNotExist
from django.utils import safestring
from django.contrib.sites.shortcuts import get_current_site

from . import stats


class InvocationError(ValueError):
    pass


class Command(object):
    show_in_help = True

    def handle(self, sender, *args, **kwargs):
        context = {
            'sender': sender,
            'args': args,
            'kwargs': kwargs,
        }
        context.update(self.get_additional_context(sender, *args, **kwargs))
        additional = self.process(sender, *args, **kwargs)
        context['process'] = additional
        return self.render_to_status(
            self.get_template_name(*args, **kwargs),
            context)

    def process(self, sender, *args, **kwargs):
        return {}

    def get_additional_context(self, sender, *args, **kwargs):
        return {
            'base_url': ''.join(['https://', get_current_site(None).domain])
        }

    def get_template_name(self, *args, **kwargs):
        return 'bot/commands/{}.txt'.format(self.code)

    def render_to_status(self, template_name, context):
        t = loader.get_template(template_name)
        return safestring.mark_safe(t.render(context).strip())


class Help(Command):
    code = 'help'
    description = "Get help about the bot."


class Unknown(Command):
    code = 'unknown'
    show_in_help = False


class Error(Command):
    code = 'error'
    show_in_help = False


class Stats(Command):
    code = 'stats'
    description = 'Return overview data about a given metric.'
    usages = [
        {
            'snippet': stat.code,
            'description': stat.description
        }
        for stat in stats.stats.values()
    ]

    def get_template_name(self, *args, **kwargs):
        return 'bot/commands/stats/{}.txt'.format(args[0])

    def get_additional_context(self, sender, *args, **kwargs):
        context = super().get_additional_context(sender, *args, **kwargs)
        try:
            stat = stats.stats[args[0]]
        except (KeyError, IndexError):
            raise InvocationError

        context['stats'] = stat.get()
        return context


commands = collections.OrderedDict()
commands['help'] = Help()
commands['stats'] = Stats()
commands['unknown'] = Unknown()
commands['error'] = Error()
