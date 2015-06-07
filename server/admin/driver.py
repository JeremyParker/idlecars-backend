# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from server import models
from server.admin.booking import BookingInline
from server.admin.user_account import UserAccountInline

class UserAccountInline(admin.StackedInline):
    model = models.UserAccount
    verbose_name = "Contact Info"
    fieldsets = (
        (None, {
            'fields': (
                ('first_name', 'last_name'),
                ('phone_number'),
                ('email'),
            )
        }),
    )
    def get_extra(self, request, obj=None, **kwargs):
        return 0


class DriverAdmin(admin.ModelAdmin):
    list_display = [
        'link_name',
        'documentation_complete',
        'booking_count',
    ]
    list_filter = [
        'documentation_complete'
    ]
    search_fields = [
        'user_account__first_name',
        'user_account__last_name',
        'user_account__phone_number',
        'user_account__email',
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
    inlines = [
        UserAccountInline,
        BookingInline,
    ]
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
