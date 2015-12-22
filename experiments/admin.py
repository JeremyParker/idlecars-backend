# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.db.models import Sum
from django.utils import timezone

import models


class AdminMixin:
    can_delete = False

    def has_delete_permission(self, request, obj=None):
        if self.can_delete:
            return super(ModelAdmin, self).has_delete_permission(request, obj)
        else:
            return False

    def get_object_from_request(self, request):
        object_id = request.META['PATH_INFO'].strip('/').split('/')[-1]
        try:
            object_id = int(object_id)
        except ValueError:
            return None
        return self.model.objects.get(pk=object_id)


class ModelAdmin(admin.ModelAdmin, AdminMixin):
    pass


class TabularInline(admin.TabularInline, AdminMixin):
    pass


class AlternativeInline(TabularInline):
    model = models.Alternative
    fields = (
        'identifier',
        'ratio',
        'participant_count',
        'conversion_count',
    )
    readonly_fields = (
        'participant_count',
        'conversion_count',
    )
    extra = 0
    max_num = 4


class ExperimentAdmin(ModelAdmin):
    list_display = (
        'identifier',
        'start_time',
        'end_time',
        'live',
        'default',
        'winner',
    )
    fields = (
        'identifier',
        'description',
        'start_time',
        'end_time',
        'live',
        'default',
        'winner',
    )
    readonly_fields = (
        'live',
        # 'participant_count',
        # 'conversion_count',
    )
    inlines = [
        AlternativeInline,
    ]

    # def get_queryset(self, request):
    #     queryset = super(ExperimentAdmin, self).get_queryset(request)
    #     queryset = queryset.annotate(
    #         participant_count=Sum('alternative__participant_count'),
    #         conversion_count=Sum('alternative__conversion_count'),
    #     )
    #     return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('default', 'winner'):
            obj = self.get_object_from_request(request)
            conditions = {
                'experiment': obj
            }
            kwargs['queryset'] = models.Alternative.objects.filter(**conditions)
        return super(ExperimentAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def live(self, instance):
        return (not instance.start_time or instance.start_time < timezone.now()) and \
            (not instance.end_time or instance.end_time > timezone.now())
    live.admin_order_field = 'live'
    live.boolean = True
    live.short_description = "Live"


admin.site.register(models.Experiment, ExperimentAdmin)
