# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from config import models


class ConfigAdmin(admin.ModelAdmin):
    ordering = ['key']
    list_display = ('key', 'data_type', 'units', 'value', 'comment')
    search_fields = ["key", "value", "comment"]
    fieldsets = (
        (None, {
            'fields': (('key',), ('data_type', 'units'), 'value', 'comment')
        }),
    )

admin.site.register(models.Config, ConfigAdmin)
