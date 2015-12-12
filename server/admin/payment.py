# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from idlecars.admin_helpers import link
from server import models
from server.services import payment as payment_service
from server.admin import BraintreeRequestInline


class PaymentAdmin(admin.ModelAdmin):
    can_delete = False
    fieldsets = (
        (None, {
            'fields': (
                ('invoice_description', 'booking_link',),
                ('amount', 'service_fee', 'credit_amount', 'idlecars_supplement', ),
                ('created_time', 'status', 'error_message',),
                ('payment_method_link', 'gateway_link', 'idlecars_supplement_link'),
                ('notes',),
            )
        }),
    )

    readonly_fields = [
        'created_time',
        'booking_link',
        'invoice_description',
        'amount',
        'service_fee',
        'payment_method_link',
        'status',
        'error_message',
        'gateway_link',
        'idlecars_supplement_link',
    ]
    inlines = [BraintreeRequestInline,]
    list_display = ('created_time', 'invoice_description', 'booking_link', 'amount', 'status')
    date_hierarchy = 'created_time'
    search_fields = [
        'transaction_id',
    ]
    list_filter = ['status']

    def booking_link(self, instance):
        return link(instance.booking)
    booking_link.short_description = 'Booking'

    def gateway_link(self, instance):
        return payment_service.details_link(instance)
    gateway_link.short_description = 'Gateway link'

    def idlecars_supplement_link(self, instance):
        return payment_service.idlecars_supplement_link(instance)

    def payment_method_link(self, instance):
        return link(instance.payment_method)
    payment_method_link.short_description = 'Payment method'

    def queryset(self, request):
        return super(PaymentAdmin, self).queryset(request).select_related(
            'booking',
            'booking__driver',
            'booking__car',
            'booking__car__make_model',
        )


class PaymentInline(admin.TabularInline):
    model = models.Payment
    verbose_name = 'Payments'
    extra = 0
    can_delete = False
    fields = ['time_link', 'invoice_description', 'amount', 'credit_amount', 'status', 'payment_method']
    readonly_fields = ['time_link', 'invoice_description', 'amount', 'credit_amount', 'status', 'payment_method']
    def time_link(self, instance):
        return link(instance, instance.created_time.strftime("%b %d, %Y %H:%M:%S"))
    def gateway_link(self, instance):
        return payment_service.details_link(instance)
    gateway_link.short_description = 'Gateway link'
