# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from credit import models

class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'invitor_code',
        'invitor_credited',
        'invite_code',
        'app_credit',
        'username',
    ]
    search_fields = [
        'user__username',
    ]
    def username(self, instance):
        return instance.user.username


admin.site.register(models.CreditCode)
admin.site.register(models.Customer, CustomerAdmin)
