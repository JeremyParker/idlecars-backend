# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from owner_crm import models

from campaign import Campaign


admin.site.register(models.Campaign, Campaign)
admin.site.register(models.Message)
