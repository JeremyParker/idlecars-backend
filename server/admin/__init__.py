# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from server import models

from braintree_request import BraintreeRequestInline
from car import CarAdmin
from booking import BookingAdmin
from owner import OwnerAdmin
from driver import DriverAdmin
from make_model import MakeModelAdmin
from payment import PaymentAdmin
from payment_method import PaymentMethodAdmin
from rideshare_flavor import RideshareFlavorAdmin


admin.site.register(models.Owner, OwnerAdmin)
admin.site.register(models.Car, CarAdmin)
admin.site.register(models.Booking, BookingAdmin)
admin.site.register(models.MakeModel, MakeModelAdmin)
admin.site.register(models.Driver, DriverAdmin)
admin.site.register(models.Insurance)
admin.site.register(models.Payment, PaymentAdmin)
admin.site.register(models.PaymentMethod)
admin.site.register(models.RideshareFlavor, RideshareFlavorAdmin)
admin.site.register(models.BraintreeRequest)

admin.site.site_header = "idlecars operations"
admin.site.site_title = ''
admin.site.index_title = ''
