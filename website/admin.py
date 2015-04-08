# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

import models

class ContactAdmin(admin.ModelAdmin):
    fields = [
        'email',
        'role_name',
        'zipcode',
        'created_time',
    ]
    list_display = [
        'email',
        'role_name',
        'zipcode',
        'created_time',
    ]
    readonly_fields = [
        'email',
        'role_name',
        'zipcode',
        'created_time',
    ]

    def role_name(self, instance):
        return unicode(instance.role)

admin.site.register(models.Contact, ContactAdmin)
