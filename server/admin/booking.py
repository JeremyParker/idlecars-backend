# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from idlecars.admin_helpers import link

from server import models


class BookingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                ('state', 'driver_docs_uploaded',),
                ('driver_link', 'driver_phone', 'driver_email',),
                ('car_link', 'car_plate', 'car_cost',),
                ('owner_link', 'owner_phone', 'owner_email',),
                ('created_time', 'end_time',),
                'notes',
            ),
        }),
    )
    list_display = [
        'state',
        'driver_docs_uploaded',
        'driver_link',
        'car_link',
        'owner_link',
        'car_cost',
        'car_insurance',
        'created_time',
    ]
    readonly_fields = [
        'driver_docs_uploaded',
        'driver',
        'car_link',
        'car_plate',
        'car_cost',
        'car_insurance',
        'owner_link',
        'owner_phone',
        'owner_email',
        'driver_link',
        'driver_phone',
        'driver_email',
        'created_time',
    ]
    search_fields = [
        'driver__auth_user__username',
        'driver__auth_user__email',
        'driver__auth_user__first_name',
        'driver__auth_user__last_name',
    ]

    def owner_link(self, instance):
        if instance.car and instance.car.owner:
            return link(instance.car.owner, instance.car.owner.__unicode__())
        else:
            return None
    owner_link.short_description = 'Owner'

    def owner_phone(self, instance):
        if instance.car and instance.car.owner:
            return instance.car.owner.phone_number()
        else:
            return None
    owner_phone.short_description = 'Phone Number'

    def owner_email(self, instance):
        if instance.car and instance.car.owner:
            return instance.car.owner.email()
        else:
            return None
    owner_email.short_description = 'Email'

    def driver_docs_uploaded(self, instance):
        if instance.driver:
            return instance.driver.all_docs_uploaded()
        return False
    driver_docs_uploaded.short_description = "Docs uploaded"

    def driver_link(self, instance):
        if instance.driver:
            return link(instance.driver, instance.driver.admin_display())
        else:
            return None
    driver_link.short_description = 'Driver'

    def car_link(self, instance):
        if instance.car:
            return link(instance.car, instance.car.__unicode__())
        else:
            return None
    car_link.short_description = 'Car'

    def car_plate(self, instance):
        if instance.car:
            return instance.car.plate
        else:
            return None
    car_plate.short_description = 'Plate'

    def car_cost(self, instance):
        if instance.car:
            return '${}'.format(instance.car.solo_cost)
        else:
            return None
    car_cost.short_description = 'Rent'
    car_cost.admin_order_field = 'car__solo_cost'

    def car_insurance(self, instance):
        return instance.car.insurance
    car_insurance.admin_order_field = 'car__insurance'


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


class BookingForCarInline(admin.TabularInline):
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
        'driver',
        'created_time',
    ]
    def detail_link(self, instance):
        return link(instance, 'details')
    can_delete = False
    def has_add_permission(self, request):
        return False


class BookingForDriverInline(admin.TabularInline):
    model = models.Booking
    verbose_name = "Booking"
    extra = 0
    fields = [
        'detail_link',
        'state',
        'car',
        'created_time',
    ]
    readonly_fields = [
        'detail_link',
        'car',
        'created_time',
    ]
    def detail_link(self, instance):
        return link(instance, 'details')
    can_delete = False
    def has_add_permission(self, request):
        return False
