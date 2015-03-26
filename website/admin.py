# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

import models

admin.site.register(models.DriverProspect)
admin.site.register(models.OwnerProspect)
admin.site.register(models.DriverSurvey)
admin.site.register(models.OwnerSurvey)
