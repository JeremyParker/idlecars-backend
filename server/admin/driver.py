# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import auth

from idlecars.reverse_admin import ReverseModelAdmin
from server import models
from server.admin.booking import BookingForDriverInline


class DriverAdmin(ReverseModelAdmin):
    inline_type = 'tabular'
    inline_reverse = (
        ('auth_user', {
            'fieldsets': (
                (None, {
                    'fields': (
                        ('first_name', 'last_name', 'username', 'email'),
                    )
                }),
            ),
            'exclude': ()
        }),
    )
    list_display = [
        'link_name',
        'phone_number',
        'email',
        'all_docs_uploaded',
        'documentation_approved',
        'booking_count',
        'date_joined',
    ]
    list_filter = [
        'documentation_approved',
    ]
    search_fields = [
        'auth_user__first_name',
        'auth_user__last_name',
        'auth_user__username',
        'auth_user__email',
    ]
    fieldsets = (
        ('Documentation', {
            'fields': (
                ('documentation_approved'),
                ('driver_license_image', 'dmv_link'),
                ('fhv_license_image', 'fhv_link'),
                ('defensive_cert_image', 'dd_link'),
                ('address_proof_image', 'poa_link'),
            )
        }),
        ('None', {
            'fields': (
                'date_joined',
               ('notes'),
            ),
        }),
    )
    readonly_fields = [
        'date_joined',
        'full_name',
        'dmv_link',
        'fhv_link',
        'dd_link',
        'poa_link',
    ]
    inlines = [BookingForDriverInline,]
    change_form_template = "change_form_inlines_at_top.html"

    def date_joined(self, instance):
        return instance.auth_user.date_joined.date()
    date_joined.short_description = 'signup date'

    def link_name(self, instance):
        return instance.admin_display()
    link_name.short_description = "Driver"

    def booking_count(self, instance):
        return models.Booking.objects.filter(driver=instance).count()

    def dmv_link(self, instance):
        return '<a href={} target="new">View Image</a>'.format(instance.driver_license_image)
    dmv_link.short_description = ''
    dmv_link.allow_tags = True

    def fhv_link(self, instance):
        return '<a href={} target="new">View Image</a>'.format(instance.fhv_license_image)
    fhv_link.short_description = ''
    fhv_link.allow_tags = True

    def dd_link(self, instance):
        return '<a href={} target="new">View Image</a>'.format(instance.defensive_cert_image)
    dd_link.short_description = ''
    dd_link.allow_tags = True

    def poa_link(self, instance):
        return '<a href={} target="new">View Image</a>'.format(instance.address_proof_image)
    poa_link.short_description = ''
    poa_link.allow_tags = True
