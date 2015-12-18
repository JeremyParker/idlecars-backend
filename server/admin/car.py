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


class NoPlateFilter(admin.SimpleListFilter):
    '''
    Filter to show cars based on if we have the plate for the car.
    '''
    title = 'plate'
    parameter_name = 'plate'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'yes'),
            ('no', 'no'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(plate='')
        elif self.value() == 'no':
            return queryset.filter(plate='')


class InsuranceFilter(admin.SimpleListFilter):
    title = 'Insurance'
    parameter_name = 'insurance'

    def lookups(self, request, model_admin):
        lookups = []
        list_of_insurances = models.Insurance.objects.all()
        for ins in list_of_insurances:
            lookups.append((
                ins.pk,
                ins.insurer_name,
            ))
        return tuple(lookups)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(insurance_id=self.value())
        else:
            return queryset


class CarAdmin(admin.ModelAdmin):
    list_display = [
        'description',
        'weekly_rent',
        'owner_link',
        'owner_rating',
        'last_status_update',
        'plate',
        'insurance',
        'shift',
    ]
    list_filter = [
        CarStaleListFilter,
        InsuranceFilter,
        'owner__rating',
        NoPlateFilter,
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
                ('exterior_color', 'interior_color'),
                ('owner', 'owner_link', 'owner_rating'),
                ('insurance', 'insurance_link', 'insurance_policy_number'),
                ('last_known_mileage', 'last_mileage_update'),
                ('effective_status', 'last_status_update', 'next_available_date',),
                ('shift', 'weekly_rent', 'deposit'),
                'min_lease',
                'notes',
                'work_with',
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
        'insurance_link',
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

    def insurance_link(self, instance):
        if instance.insurance:
            return link(instance.insurance, instance.insurance.__unicode__())
        else:
            return None
    insurance_link.short_description = 'Insurance'

    def owner_rating(self, instance):
        if instance.owner and instance.owner.rating:
            return models.Owner.RATING[instance.owner.rating][1]
        else:
            return 'unrated'
