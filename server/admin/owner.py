# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

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


class OwnerAdmin(admin.ModelAdmin):
    inlines = [
        UserAccountForOwnerInline,
        CarInline,
    ]
    fieldsets = (
        (None, {
            'fields': (
                ('split_shift', 'rating'),
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
        'rating',
        'number',
        'email',
        'cars_available',
        'total_cars',
    ]
    search_fields = [
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
