# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class MakeModel(models.Model):
    make = models.CharField(max_length=128, blank=True)
    model = models.CharField(max_length=128, blank=True)
    def __unicode__(self):
        return '{} {}'.format(self.make, self.model)
