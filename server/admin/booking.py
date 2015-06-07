# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from idlecars.admin_helpers import link

from server import models


class BookingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                ('driver_link', 'driver_phone', 'driver_email'),
                'state',
                'car_link',
                'owner_link',
                'created_time',
                'notes',
            ),
        }),
    )
    list_display = [
        'state',
        'driver_link',
        'car_link',
        'owner_link',
        'created_time',
    ]
    readonly_fields = [
        'driver',
        'car_link',
        'owner_link',
        'driver_link',
        'driver_phone',
        'driver_email',
        'created_time',
    ]

    def owner_link(self, instance):
        if instance.car and instance.car.owner:
            return link(instance.car.owner, instance.car.owner.__unicode__())
        else:
            return None
    owner_link.short_description = 'Owner'

    def driver_link(self, instance):
        if instance.driver:
            return link(instance.driver, instance.driver.full_name())
        else:
            return None
    driver_link.short_description = 'Driver'

    def car_link(self, instance):
        if instance.car:
            return link(instance.car, instance.car.__unicode__())
        else:
            return None
    car_link.short_description = 'Car'

    def driver_phone(self, instance):
        if instance.driver:
            return instance.driver.phone_number()
        else:
            return None

    def driver_email(self, instance):
        if instance.driver:
            return instance.driver.email()
        else:
            return None


class BookingInline(admin.TabularInline):
    model = models.Booking
    verbose_name = "Booking"
    extra = 0
    fields = [
        'detail_link',
        'state',
        'driver',
        'created_time',
    ]
    readonly_fields = [
        'detail_link',
        'state',
        'driver',
        'created_time',
    ]
    def detail_link(self, instance):
        return link(instance, 'details')
    can_delete = False
    def has_add_permission(self, request):
        return False
