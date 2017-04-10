from django.contrib import admin


from . import models


@admin.register(models.Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'url',
        'up',
        'open_registrations',
        'https_score',
        'last_fetched',

    ]
