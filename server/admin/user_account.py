# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from server import models

class UserAccountInline(admin.StackedInline):
    model = models.UserAccount
    verbose_name = "Contact"

    # If there are 0 user_accounts, show an extra inline form for entry
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1
