from . import models


def releases(*args, **kwargs):
    return {
        'current_release': models.Release.objects.order_by('_version').last()
    }
