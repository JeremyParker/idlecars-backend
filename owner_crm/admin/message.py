# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from idlecars.admin_helpers import link


class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'created_time',
        'campaign',
        'owner',
        'car',
        'driver_link',
        'booking',
    ]

    def driver_link(self, instance):
        if instance.driver:
            return link(instance.driver, instance.driver.admin_display())
        else:
            return None
    driver_link.short_description = 'Driver'
