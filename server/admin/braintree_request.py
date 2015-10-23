# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from server import models


class BraintreeRequestInline(admin.TabularInline):
    model = models.BraintreeRequest
    verbose_name = 'Requests'
    extra = 0
    can_delete = False
    fields = [
        'created_time',
        'payment',
        'payment_method',
        'request',
        'response',
    ]
    readonly_fields = [
        'created_time',
        'payment',
        'payment_method',
        'request',
        'response',
    ]
    def time_link(self, instance):
        return link(instance, instance.created_time.strftime("%b %d, %Y %H:%M:%S"))
