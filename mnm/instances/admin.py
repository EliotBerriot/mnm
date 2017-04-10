from django.contrib import admin


from . import models


def push_to_influxdb(modeladmin, request, queryset):
    for row in queryset:
        row.push_to_influxdb()


@admin.register(models.Instance)
class InstanceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'url',
        'users',
        'statuses',
        'up',
        'open_registrations',
        'https_score',
        'last_fetched',
    ]

    search_fields = ['name']

    actions = [push_to_influxdb]
