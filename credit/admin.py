# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from credit import models

class CustomerAdmin(admin.ModelAdmin):
    readonly_fields = [
        'user',
        'invite_code',
        'invitor_code',
        'invitor_credited',
    ]
    list_display = [
        'user',
        'invitor_code',
        'invitor_credited',
        'invite_code',
        'app_credit',
    ]
    search_fields = [
        'user__username',
    ]
    def username(self, instance):
        return instance.user.username

class CreditCodeAdmin(admin.ModelAdmin):
    list_display = [
        'created_time',
        'description',
        'credit_code',
        'credit_amount',
        'invitor_credit_amount',
        'redeem_count',
        'expiry_time',
    ]
    search_fields = [
        'customer__user__username',
        'description',
        'credit_code',
    ]
    readonly_fields = [
        'redeem_count',
    ]

admin.site.register(models.CreditCode, CreditCodeAdmin)
admin.site.register(models.Customer, CustomerAdmin)
