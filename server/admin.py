# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from server import models, admin_classes


admin.site.register(models.Owner, admin_classes.OwnerAdmin)
admin.site.register(models.Car, admin_classes.CarAdmin)
admin.site.register(models.Booking, admin_classes.BookingAdmin)
admin.site.register(models.MakeModel)

admin.site.site_header = "idlecars operations"
admin.site.site_title = ''
admin.site.index_title = ''
