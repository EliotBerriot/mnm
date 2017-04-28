from django.contrib import admin


from . import models


@admin.register(models.Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = [
        'tag',
        'url',
        'release_date',
    ]

    search_fields = ['tag', 'body']
