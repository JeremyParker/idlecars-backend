# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


class CampaignAdmin(admin.ModelAdmin):
    fields = [
        'name',
        'preferred_medium',
        'notes',
    ]
    list_display = [
        'name',
        'notes',
        'preferred_medium',
    ]
