# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from server.admin import BraintreeRequestInline


class PaymentMethodAdmin(admin.ModelAdmin):
    can_delete = False
    search_fields = [
        'gateway_token',
    ]
    inlines = [BraintreeRequestInline]
