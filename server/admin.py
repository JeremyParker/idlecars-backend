# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
import models as models


class UserAccountInline(admin.StackedInline):
    model = models.UserAccount
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1


class OwnerAdmin(admin.ModelAdmin):
    inlines = [
        UserAccountInline,
    ]
    fieldsets = (
        (None, {
            'fields': (
                ('split_shift', 'rating'),
                'last_engagement',
                'notes',
                'company_name',
                'address1',
                'address2',
                ('city', 'state_code', 'zipcode'),
            )
        }),
    )
    list_display = [
        'name',
        'rating',
    ]
    change_form_template = "change_form_inlines_at_top.html"

admin.site.register(models.Owner, OwnerAdmin)
admin.site.register(models.Car)

admin.site.site_header = "Idle Cars Operations"
admin.site.site_title = ''
admin.site.index_title = ''
