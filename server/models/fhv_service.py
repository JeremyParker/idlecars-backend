# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class FhvProvider(models.Model):
    name = models.CharField(max_length=128, blank=False)
    compatible_models = models.ManyToManyField(MakeModel)

    def __unicode__(self):
        return self.name
