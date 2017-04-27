from . import models


def instances_count(*args, **kwargs):
    return {
        'instances_count': models.Instance.objects.public().count()
    }
