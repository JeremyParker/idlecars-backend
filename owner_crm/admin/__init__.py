# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from owner_crm import models

from campaign import CampaignAdmin
from message import MessageAdmin


admin.site.register(models.Campaign, CampaignAdmin)
admin.site.register(models.Message, MessageAdmin)
