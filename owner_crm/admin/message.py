# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'created_time',
        'campaign',
        'owner',
        'car',
        'driver',
        'booking',
    ]
