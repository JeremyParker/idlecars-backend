# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.conf import settings

from idlecars.admin_helpers import link

from server import models
from server.admin.user_account import UserAccountForOwnerInline


class CarInline(admin.TabularInline):
    model = models.Car
    verbose_name = "Cars"
    extra = 0
    fields = [
        'detail_link',
        'make_model',
        'year',
        'status',
        'next_available_date',
        'solo_cost',
        'solo_deposit',
        'split_cost',
        'split_deposit',
        'min_lease',
    ]
    readonly_fields = ['detail_link']
    def detail_link(self, instance):
        return link(instance, 'details')


class AuthUserInline(admin.TabularInline):
    model = models.Owner.auth_users.through
    verbose_name = "Users"
    extra = 0
    can_delete = False
    fields = [
        'detail_link',
        'first_name',
        'last_name',
        'phone_number',
        'email',
    ]
    readonly_fields = [
        'detail_link',
        'first_name',
        'last_name',
        'phone_number',
        'email',
    ]
    def detail_link(self, instance):
        return link(instance.user, 'details')

    def first_name(self, instance):
        return instance.user.first_name

    def last_name(self, instance):
        return instance.user.last_name

    def phone_number(self, instance):
        return instance.user.username

    def email(self, instance):
        return instance.user.email


class OwnerAdmin(admin.ModelAdmin):
    inlines = [
        AuthUserInline,
        UserAccountForOwnerInline,
        CarInline,
    ]
    fieldsets = (
        (None, {
            'fields': (
                ('split_shift', 'rating'),
                ('merchant_id', 'merchant_account_state',),
                ('service_percentage', 'effective_service_percentage',),
                'notes',
                'company_name',
                'address1',
                'address2',
                ('city', 'state_code', 'zipcode'),
            )
        }),
    )
    readonly_fields = ['merchant_id', 'merchant_account_state', 'effective_service_percentage',]
    if settings.DEBUG:
        readonly_fields = ['merchant_id', 'effective_service_percentage',]

    list_display = [
        'link_name',
        'rating',
        'phone_number',
        'email',
        'cars_available',
        'total_cars',
        'merchant_account_state',
    ]
    search_fields = [
        # TDOO - free ourselves from user_account alltogether
        'user_account__last_name',
        'user_account__first_name',
        'user_account__phone_number',
        'user_account__email',
        'company_name',
    ]
    change_form_template = "change_form_inlines_at_top.html"
    def link_name(self, instance):
        return instance.__unicode__()
    link_name.short_description = "Name"

    def cars_available(self, instance):
        return instance.cars.filter(status='available').count()

    def total_cars(self, instance):
        return instance.cars.count()
