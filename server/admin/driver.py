# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import auth

from idlecars.reverse_admin import ReverseInlineModelAdmin, ReverseModelAdmin
from server import models
from server.admin.booking import BookingForDriverInline
from server.admin.user_account import UserAccountForDriverInline


class DriverAdmin(ReverseModelAdmin):
    inline_type = 'tabular'
    inline_reverse = (
        ('auth_user', {
            'fieldsets': (
                (None, {
                    'fields': (
                        ('first_name', 'last_name'),
                        ('username'),
                        ('email'),
                    )
                }),
            ),
            'exclude': ()
        }),
    )
    list_display = [
        'link_name',
        'documentation_complete',
        'booking_count',
    ]
    list_filter = [
        'documentation_complete'
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
                ('documentation_complete'),
                ('dmv_license'),
                ('fhv_license'),
                ('dd_cert'),
                ('proof_of_address'),
            )
        }),
    )
    readonly_fields = [
        'full_name',
        'dmv_license',
        'fhv_license',
        'dd_cert',
        'proof_of_address',
    ]
    inlines = [BookingForDriverInline,]
    change_form_template = "change_form_inlines_at_top.html"

    def link_name(self, instance):
        return instance.user_account.full_name()
    link_name.short_description = "Name"

    def booking_count(self, instance):
        return models.Booking.objects.filter(driver=instance).count()

    def dmv_license(self, instance): return 'placeholder'
    def fhv_license(self, instance): return 'placeholder'
    def dd_cert(self, instance): return 'placeholder'
    def proof_of_address(self, instance): return 'placeholder'
