# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from idlecars.admin_helpers import link
from server import models
from server.services import payment as payment_service


class PaymentAdmin(admin.ModelAdmin):
    can_delete = False
    fieldsets = (
        (None, {
            'fields': (
                'booking_link',
                ('created_time', 'invoice_item',),
                ('status', 'error_message',),
                ('amount', 'service_fee', 'payment_method',),
                ('transaction_id', 'gateway_link',),
            )
        }),
    )

    readonly_fields = [
        'created_time',
        'booking_link',
        'invoice_item',
        'amount',
        'service_fee',
        'payment_method',
        'status',
        'error_message',
        'transaction_id',
        'gateway_link',
    ]
    list_display = ('created_time', 'invoice_item', 'booking_link', 'amount', 'status')
    date_hierarchy = 'created_time'
    search_fields = [
        'booking__driver__first_name',
        'booking__driver__last_name'
        'transaction_id',
    ]
    list_filter = ['status']

    def invoice_item(self, instance):
        return instance.week_ending or 'Deposit'

    def booking_link(self, instance):
        return link(instance.booking)
    booking_link.short_description = 'Booking'

    def gateway_link(self, instance):
        return payment_service.details_link(instance)
    gateway_link.short_description = 'Gateway link'

    def queryset(self, request):
        return super(PaymentAdmin, self).queryset(request).prefetch_related(
            'booking',
            'booking__driver',
            'booking__car',
            'booking__payment_method',
        )


class PaymentInline(admin.TabularInline):
    model = models.Payment
    verbose_name = 'Payments'
    extra = 0
    can_delete = False
    fields = ['time_link', 'invoice_item', 'amount', 'status', 'payment_method']
    readonly_fields = ['time_link', 'invoice_item', 'amount', 'status', 'payment_method']
    def time_link(self, instance):
        return link(instance, instance.created_time.strftime("%b %d, %Y %H:%M:%S"))
    def invoice_item(self, instance):
        return instance.week_ending or 'Deposit'
