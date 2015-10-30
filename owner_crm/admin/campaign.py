# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


class Campaign(admin.ModelAdmin):
    fields = [
        'name',
        'preferred_method',
        'notes',
    ]
    readonly_fields = ['name']

    list_display = [
        'name',
        'preferred_method',
    ]
