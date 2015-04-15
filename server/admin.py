# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
import django.utils
from django.core import urlresolvers

import models as models

# helper to make links on admin pages
def link(obj, text=None):
    if text is None:
        text = unicode(obj)
    if obj.pk:
        view = "admin:{0}_{1}_change".format(obj._meta.app_label, obj._meta.module_name)
        view_url = urlresolvers.reverse(view, args=(obj.pk,))
    else:
        view = "admin:{0}_{1}_add".format(obj._meta.app_label, obj._meta.module_name)
        view_url = urlresolvers.reverse(view, args=())
    a_str = '<a href="{view_url}">{text}</a>'.format(view_url=view_url, text=text)
    return django.utils.safestring.mark_safe(a_str)


class UserAccountInline(admin.StackedInline):
    model = models.UserAccount
    verbose_name = "Contact"
    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 0
        return 1


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
    def status_date(self, instance):
        if instance.owner:
            return instance.owner.last_engagement


class OwnerAdmin(admin.ModelAdmin):
    inlines = [
        UserAccountInline,
        CarInline,
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
        'link_name',
        'rating',
        'number',
        'email',
        'cars_available',
        'total_cars',
    ]
    change_form_template = "change_form_inlines_at_top.html"
    def link_name(self, instance):
        return instance.__unicode__()
    link_name.short_description = "Name"

    def cars_available(self, instance):
        return instance.cars.filter(status='available').count()

    def total_cars(self, instance):
        return instance.cars.count()


class CarAdmin(admin.ModelAdmin):
    list_display = [
        'description',
        'effective_status',
        'solo_cost',
        'split_cost',
        'owner_link',
        'owner_rating',
    ]
    fieldsets = (
        (None, {
            'fields': (
                ('make_model', 'year', 'plate'),
                ('owner', 'owner_link', 'owner_rating'),
                ('status', 'status_date', 'next_available_date'),
                ('solo_cost', 'solo_deposit'),
                ('split_cost', 'split_deposit'),
                'min_lease',
                'notes',
            )
        }),
    )
    readonly_fields = [
        'owner_link',
        'owner_rating',
        'status_date',
        'effective_status',
    ]

    def description(self, instance):
        return instance.__unicode__()
    def owner_link(self, instance):
        if instance.owner:
            return link(instance.owner, instance.owner.__unicode__())
        else:
            return None
    owner_link.short_description = 'Owner'

    def owner_rating(self, instance):
        if instance.owner:
            return instance.owner.rating

    def status_date(self, instance):
        if instance.owner:
            return instance.owner.last_engagement


admin.site.register(models.Owner, OwnerAdmin)
admin.site.register(models.Car, CarAdmin)
admin.site.register(models.MakeModel)

admin.site.site_header = "Idle Cars Operations"
admin.site.site_title = ''
admin.site.index_title = ''
