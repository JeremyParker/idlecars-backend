# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


class OnboardingOwnerAdmin(admin.ModelAdmin):
    fields = [
        'phone_number',
        'name',
        'published_date',
        'created_time',
    ]
    list_display = [
        'phone_number',
        'name',
        'published_date',
        'created_time',
    ]
    readonly_fields = [
        'created_time',
    ]

