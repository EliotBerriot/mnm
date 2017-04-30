from django.contrib import admin


from . import models


@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'creation_date',
        'last_modification_date',
        'sort_order',
        'status',
    ]

    list_filter = [
        'status',
    ]
    list_editable = [
        'sort_order',
        'status',
    ]

    search_fields = ['title', 'content']
