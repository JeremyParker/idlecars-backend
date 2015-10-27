# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from idlecars.admin_helpers import link
from server import models
from server.admin import BraintreeRequestInline
from server.services import payment as payment_service


class PaymentMethodMixin(object):
    def detail_link(self, instance):
        return link(instance, '{}: **** **** **** {}'.format(instance.card_type, instance.suffix))

    def gateway_link(self, instance):
        return payment_service.payment_method_link(instance)
    gateway_link.short_description = "Token"

    def driver_link(self, instance):
        if instance.driver:
            return link(instance.driver, instance.driver.admin_display())
        else:
            return None
    driver_link.short_description = 'Driver'


class PaymentMethodAdmin(admin.ModelAdmin, PaymentMethodMixin):
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
        'detail_link',
        'gateway_link',
        'driver_link',
    ]
    readonly_fields = [
        'detail_link',
        'gateway_link',
        'driver_link',
        'expiration_date',
        'suffix',
        'card_type',
    ]


class PaymentMethodInline(admin.TabularInline, PaymentMethodMixin):
    model = models.PaymentMethod
    verbose_name = "Payment Method"
    can_delete = False
    extra = 0
    fields = [
        'detail_link', 'gateway_link',
    ]
    readonly_fields = [
        'gateway_link', 'detail_link',
    ]
