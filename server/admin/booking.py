# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from idlecars.admin_helpers import link

from server import models
from server.admin.payment import PaymentInline


class BookingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                ('state', 'driver_docs_uploaded',),
                ('driver_link', 'driver_phone', 'driver_email',),
                ('car_link', 'car_plate', 'car_cost', 'effective_service_percentage',),
                ('owner_link', 'owner_phone', 'owner_email',),
                ('base_letter','base_letter_link'),
            ),
        }),
        ('State History', {
            'fields': (
                ('created_time',),
                ('checkout_time',),
                ('requested_time',),
                ('approval_time',),
                ('pickup_time',),
                ('end_time',),
                ('return_time',),
                ('incomplete_time', 'incomplete_reason',),
                ('refund_time',),
            ),
        }),
        ('Notes', {
            'fields': (
                'notes',
                'deprecated_state',
            ),
        }),
    )
    inlines = [PaymentInline]
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
        'state',
        'driver_docs_uploaded',
        'driver',
        'car_link',
        'car_plate',
        'car_cost',
        'effective_service_percentage',
        'car_insurance',
        'owner_link',
        'owner_phone',
        'owner_email',
        'driver_link',
        'driver_phone',
        'driver_email',
        'base_letter_link',
        'created_time',
        # 'checkout_time',
        # 'requested_time',
        # 'approval_time',
        # 'pickup_time',
        # 'end_time',
        # 'return_time',
        # 'incomplete_time',
        # 'incomplete_reason',
        # 'refund_time',
        'deprecated_state',
    ]
    search_fields = [
        'driver__auth_user__username',
        'driver__auth_user__email',
        'driver__auth_user__first_name',
        'driver__auth_user__last_name',
    ]

    def state(self, instance):
        return models.Booking.STATES[instance.get_state()]

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
            return link(instance.car, instance.car.display_name())
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
        if instance.weekly_rent:
            return '${}'.format(instance.weekly_rent)
        else:
            return instance.car.solo_cost
    car_cost.short_description = 'Rent'
    car_cost.admin_order_field = 'car__solo_cost'

    def effective_service_percentage(self, instance):
        return instance.service_percentage or instance.car.owner.effective_service_percentage
    effective_service_percentage.short_description = 'Take rate'

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

    def base_letter_link(self, instance):
        return '<a href={} target="new">View Image</a>'.format(instance.base_letter)
    base_letter_link.short_description = ''
    base_letter_link.allow_tags = True


class BookingInlineBase(admin.TabularInline):
    model = models.Booking
    verbose_name = "Booking"
    extra = 0
    def state(self, instance):
        return models.Booking.STATES[instance.get_state()]
    def detail_link(self, instance):
        return link(instance, 'details')
    can_delete = False
    def has_add_permission(self, request):
        return False


class BookingForCarInline(BookingInlineBase):
    fields = [
        'detail_link',
        'state',
        'incomplete_reason',
        'driver',
        'created_time',
    ]
    readonly_fields = [
        'detail_link',
        'state',
        'incomplete_reason',
        'driver',
        'created_time',
    ]


class BookingForDriverInline(BookingInlineBase):
    fields = [
        'detail_link',
        'state',
        'incomplete_reason',
        'car',
        'created_time',
    ]
    readonly_fields = [
        'detail_link',
        'state',
        'incomplete_reason',
        'car',
        'created_time',
    ]
