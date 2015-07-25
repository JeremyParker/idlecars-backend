# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from server.models import MakeModel


class RideshareProvider(models.Model):
    name = models.CharField(max_length=128, blank=False)
    frieldly_id = models.CharField(max_length=32, blank=False, unique=True)
    compatible_models = models.ManyToManyField(MakeModel)

    def __unicode__(self):
        return self.name
