# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from server.models import MakeModel, Car


class RideshareFlavor(models.Model):
    name = models.CharField(max_length=128, blank=False)
    friendly_id = models.CharField(max_length=32, blank=False, unique=True)
    min_year = models.IntegerField(choices=Car.YEARS, blank=True, null=True)
    compatible_models = models.ManyToManyField(MakeModel)

    def __unicode__(self):
        return self.name
