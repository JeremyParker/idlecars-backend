# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from credit import models

admin.site.register(models.CreditCode)
admin.site.register(models.Customer)
