# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from server import models

class UserAccountForDriverInline(admin.StackedInline):
    model = models.UserAccount
    verbose_name = "Contact Info"
    fieldsets = (
        (None, {
            'fields': (
                ('first_name', 'last_name'),
                ('phone_number'),
                ('email'),
            )
        }),
    )
    def get_extra(self, request, obj=None, **kwargs):
        return 0


class UserAccountForOwnerInline(admin.StackedInline):
    model = models.UserAccount
    verbose_name = "Contact"

    # If there are 0 user_accounts, show an extra inline form for entry
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1
