# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
import models as models


class UserAccountInline(admin.StackedInline):
    model = models.UserAccount


class OwnerAdmin(admin.ModelAdmin):
    inlines = [
        UserAccountInline,
    ]
    fields = [
        'company_name',
        'address1',
        'address2',
        'city',
        'state_code',
        'zipcode',
        'split_shift',
        'rating',
        'last_engagement',
        'notes',
    ]
    list_display = [
        'name',
        'rating',
    ]

admin.site.register(models.Owner, OwnerAdmin)
admin.site.register(models.Car)

admin.site.site_header = "Idle Cars Operations"
admin.site.site_title = ''
admin.site.index_title = ''
