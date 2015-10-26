# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from idlecars.admin_helpers import link
from server.admin import BraintreeRequestInline
from server.services import payment as payment_service


class PaymentMethodAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                ('suffix', 'card_type', 'expiration_date',),
                ('driver_link', 'gateway_link',),
            )
        }),
    )
    can_delete = False
    search_fields = [
        'gateway_token',
    ]
    inlines = [BraintreeRequestInline]

    list_display = [
        'link_name',
        'gateway_link',
        'driver_link',
    ]
    readonly_fields = [
        'link_name',
        'gateway_link',
        'driver_link',
        'expiration_date',
        'suffix',
        'card_type',
    ]

    def gateway_link(self, instance):
        return payment_service.payment_method_link(instance)
    gateway_link.short_description = "Token"

    def driver_link(self, instance):
        if instance.driver:
            return link(instance.driver, instance.driver.admin_display())
        else:
            return None
    driver_link.short_description = 'Driver'


    def link_name(self, instance):
        return instance.__unicode__()
    link_name.short_description = "Card"
