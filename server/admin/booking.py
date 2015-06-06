# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from idlecars.admin_helpers import link

from server import models


class BookingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'state',
                ('full_name', 'phone_number', 'email'),
                'car_link',
                'owner_link',
                'created_time',
                'notes',
            ),
        }),
    )
    list_display = [
        'state',
        'user_account',
        'car_link',
        'owner_link',
        'created_time',
    ]
    readonly_fields = [
        'user_account',
        'car_link',
        'owner_link',
        'full_name',
        'phone_number',
        'email',
        'created_time',
    ]

    def owner_link(self, instance):
        if instance.car and instance.car.owner:
            return link(instance.car.owner, instance.car.owner.__unicode__())
        else:
            return None
    owner_link.short_description = 'Owner'

    def car_link(self, instance):
        if instance.car:
            return link(instance.car, instance.car.__unicode__())
        else:
            return None
    car_link.short_description = 'Car'

    def full_name(self, instance):
        if instance.user_account:
            return instance.user_account.full_name()
        else:
            return None

    def phone_number(self, instance):
        if instance.user_account:
            return instance.user_account.phone_number
        else:
            return None

    def email(self, instance):
        if instance.user_account:
            return instance.user_account.email
        else:
            return None


class BookingInline(admin.TabularInline):
    model = models.Booking
    verbose_name = "Booking"
    extra = 0
    fields = [
        'detail_link',
        'state',
        'user_account',
        'created_time',
    ]
    readonly_fields = [
        'detail_link',
        'state',
        'user_account',
        'created_time',
    ]
    def detail_link(self, instance):
        return link(instance, 'details')
    can_delete = False
    def has_add_permission(self, request):
        return False
