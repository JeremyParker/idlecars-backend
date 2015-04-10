# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
import models as server_models


admin.site.register(server_models.Customer)
admin.site.register(server_models.Owner)
admin.site.register(server_models.Car)
