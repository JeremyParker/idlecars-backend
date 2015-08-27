# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from server import models


class Car(models.Car):
    class Meta:
        proxy = True


class Owner(models.Owner):
    class Meta:
        proxy = True


class CarAdmin(admin.ModelAdmin):
    pass
    # def queryset(self, request):
    #     owner =
    #     return self.model.objects.filter(owner=request.user)

class OwnerAdmin(admin.ModelAdmin):
    pass

admin.site.register(Owner, OwnerAdmin)
admin.site.register(Car, CarAdmin)
