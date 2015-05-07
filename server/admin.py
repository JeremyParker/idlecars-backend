# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
import django.utils
from django.core import urlresolvers

from server import models
from server import services


# helper to make links on admin pages
def link(obj, text=None):
    if text is None:
        text = unicode(obj)
    if obj.pk:
        view = "admin:{0}_{1}_change".format(obj._meta.app_label, obj._meta.model_name)
        view_url = urlresolvers.reverse(view, args=(obj.pk,))
    else:
        view = "admin:{0}_{1}_add".format(obj._meta.app_label, obj._meta.model_name)
        view_url = urlresolvers.reverse(view, args=())
    a_str = '<a href="{view_url}">{text}</a>'.format(view_url=view_url, text=text)
    return django.utils.safestring.mark_safe(a_str)


class UserAccountInline(admin.StackedInline):
    model = models.UserAccount
    verbose_name = "Contact"

    # If there are 0 user_accounts, show an extra inline form for entry
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
    search_fields = ['user_account__last_name', 'user_account__first_name', 'company_name']
    change_form_template = "change_form_inlines_at_top.html"
    def link_name(self, instance):
        return instance.__unicode__()
    link_name.short_description = "Name"

    def cars_available(self, instance):
        return instance.cars.filter(status='available').count()

    def total_cars(self, instance):
        return instance.cars.count()


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
        )

    def queryset(self, request, queryset):
        if self.value() == 'stale':
            return services.car.filter_needs_renewal(queryset)
        elif self.value() == 'live':
            return services.car.filter_live(queryset)

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


class CarAdmin(admin.ModelAdmin):
    list_display = [
        'description',
        'effective_status',
        'solo_cost',
        'solo_deposit',
        'owner_link',
        'owner_rating',
        'plate',
    ]
    list_filter = [
        CarStaleListFilter,
        'owner__rating',
        'status',
        NoPlateFilter,
    ]
    search_fields = [
        'make_model__model',
        'make_model__make',
        'year'
    ]
    fieldsets = (
        (None, {
            'fields': (
                ('make_model', 'hybrid', 'year'),
                ('plate', 'base'),
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
        if instance.owner and instance.owner.rating:
            return models.Owner.RATING[instance.owner.rating][1]
        else:
            return 'unrated'

    def status_date(self, instance):
        if instance.owner:
            return instance.owner.last_engagement


class BookingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'state',
                ('full_name', 'phone_number', 'email'),
                'car_link',
                'owner_link',
                'created_time',
                'notes',
            ),
        }),
    )
    list_display = [
        'state',
        'user_account',
        'car_link',
        'owner_link',
        'created_time',
    ]
    readonly_fields = [
        'user_account',
        'car_link',
        'owner_link',
        'full_name',
        'phone_number',
        'email',
        'created_time',
    ]

    def owner_link(self, instance):
        if instance.car and instance.car.owner:
            return link(instance.car.owner, instance.car.owner.__unicode__())
        else:
            return None
    owner_link.short_description = 'Owner'

    def car_link(self, instance):
        if instance.car:
            return link(instance.car, instance.car.__unicode__())
        else:
            return None
    car_link.short_description = 'Car'

    def full_name(self, instance):
        if instance.user_account:
            return instance.user_account.full_name()
        else:
            return None

    def phone_number(self, instance):
        if instance.user_account:
            return instance.user_account.phone_number
        else:
            return None

    def email(self, instance):
        if instance.user_account:
            return instance.user_account.email
        else:
            return None


admin.site.register(models.Owner, OwnerAdmin)
admin.site.register(models.Car, CarAdmin)
admin.site.register(models.Booking, BookingAdmin)
admin.site.register(models.MakeModel)

admin.site.site_header = "Idle Cars Operations"
admin.site.site_title = ''
admin.site.index_title = ''
