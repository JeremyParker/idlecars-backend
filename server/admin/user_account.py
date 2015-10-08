# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from server import models


class UserAccountForOwnerInline(admin.StackedInline):
    model = models.UserAccount
    verbose_name = "Contact"

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
