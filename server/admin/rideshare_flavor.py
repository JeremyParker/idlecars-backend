# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin


class RideshareFlavorAdmin(admin.ModelAdmin):
    filter_horizontal = ('compatible_models',)
