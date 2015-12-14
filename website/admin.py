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


class UserMessageAdmin(admin.ModelAdmin):
    fields = [
        'first_name',
        'email',
        'message',
        'created_time',
        'notes',
    ]
    readonly_fields = [
        'first_name',
        'email',
        'message',
        'created_time',
    ]
    list_display = [
        'first_name',
        'email',
        'message_display',
        'created_time',
    ]
    search_fields = [
        'first_name',
        'email',
        'message',
    ]

    def message_display(self, instance):
        max_display_len = 200
        if len(instance.message) > max_display_len:
            return '{}...'.format(instance.message[0:max_display_len])
        return instance.message

admin.site.register(models.Contact, ContactAdmin)
admin.site.register(models.UserMessage, UserMessageAdmin)
