# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from server import models

from car import CarAdmin
from booking import BookingAdmin
from owner import OwnerAdmin
from driver import DriverAdmin
from make_model import MakeModelAdmin

admin.site.register(models.Owner, OwnerAdmin)
admin.site.register(models.Car, CarAdmin)
admin.site.register(models.Booking, BookingAdmin)
admin.site.register(models.MakeModel, MakeModelAdmin)
admin.site.register(models.Driver, DriverAdmin)
admin.site.register(models.Insurance)
admin.site.register(models.FhvProvider)

admin.site.site_header = "idlecars operations"
admin.site.site_title = ''
admin.site.index_title = ''
