# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.conf import settings

from idlecars.admin_helpers import link

from server import models


class CarInline(admin.TabularInline):
    model = models.Car
    verbose_name = "Cars"
    extra = 0
    fields = [
        'detail_link',
        'make_model',
        'year',
        'next_available_date',
        'shift',
        'weekly_rent',
        'deposit',
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
        CarInline,
    ]
    filter_horizontal = ('auth_users',)
    fieldsets = (
        (None, {
            'fields': (
                'notes',
                'company_name',
                'address1',
                'address2',
                ('city', 'state_code', 'zipcode'),
            )
        }),
    )
    list_display = [
        'link_name',
        'phone_number',
        'email',
        'shifts_listed',
    ]
    search_fields = [
        # TDOO - free ourselves from user_account alltogether
        'user_account__last_name',
        'user_account__first_name',
        'user_account__phone_number',
        'user_account__email',
        'auth_users__last_name',
        'auth_users__first_name',
        'auth_users__username',
        'auth_users__email',
        'company_name',
    ]
    change_form_template = "change_form_inlines_at_top.html"
    def link_name(self, instance):
        return instance.__unicode__()
    link_name.short_description = "Name"

    def shifts_listed(self, instance):
        return instance.cars.count()
