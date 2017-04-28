from . import models


def releases(*args, **kwargs):
    return {
        'current_release': models.Release.objects.latest('_version')
    }
