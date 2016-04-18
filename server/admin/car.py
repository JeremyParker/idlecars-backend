# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
import django.utils
from django.core import urlresolvers

from idlecars.admin_helpers import link

from server import models
from server import services
from server.admin.booking import BookingForCarInline

from server.models import CarCompatibility


class CarStaleListFilter(admin.SimpleListFilter):
    '''
    Filter to show cars that are complete and WOULD be listed on the site, except we need to talk
    to the owner and refresh the listing.
    '''
    title = 'state'
    parameter_name = 'state'

    def lookups(self, request, model_admin):
        return (
            ('stale', 'stale'),
            ('live', 'live'),
            ('reserved', 'booking in progress'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'stale':
            return services.car.filter_needs_renewal(queryset)
        elif self.value() == 'live':
            return services.car.filter_live(queryset)
        elif self.value() == 'reserved':
            return services.car.filter_booking_in_progress(queryset)


class CarAdmin(admin.ModelAdmin):
    list_display = [
        'description',
        'owner_link',
        'last_status_update',
        'plate',
        'shift',
        'weekly_rent',
    ]
    list_filter = [
        CarStaleListFilter,
    ]
    search_fields = [
        'make_model__model',
        'make_model__make',
        'year',
        'plate',
    ]
    fieldsets = (
        (None, {
            'fields': (
                ('make_model', 'hybrid', 'year', 'plate',),
                ('owner', 'owner_link', 'owner_rating'),
                ('last_known_mileage', 'last_mileage_update'),
                ('effective_status', 'last_status_update', 'next_available_date',),
                ('shift', 'shift_details', 'weekly_rent', 'deposit'),
                'notes',
            )
        }),
        ('TLC data', {
            'fields': (
                ('found_in_tlc', 'last_updated', 'active_in_tlc',),
                ('base', 'base_number', 'base_type',),
                ('base_address', 'base_telephone_number',),
                ('registrant_name', 'expiration_date',),
                ('vehicle_vin_number',),
            )
        }),
    )
    readonly_fields = [
        'owner_link',
        'last_mileage_update',
        'owner_rating',
        'effective_status',
        'work_with',
        'found_in_tlc',
        'last_updated',
        'active_in_tlc',
        'base_number',
        'base_address',
        'base_telephone_number',
        'base_type',
        'registrant_name',
        'expiration_date',
        'vehicle_vin_number',
    ]
    inlines = [
        BookingForCarInline,
    ]

    def work_with(self, instance):
        return [str(flavor) for flavor in CarCompatibility(instance).all()]

    def description(self, instance):
        return instance.__unicode__()

    def owner_link(self, instance):
        if instance.owner:
            return link(instance.owner, instance.owner.__unicode__())
        else:
            return None
    owner_link.short_description = 'Owner'

    def owner_rating(self, instance):
        if instance.owner and instance.owner.rating:
            return models.Owner.RATING[instance.owner.rating][1]
        else:
            return 'unrated'
