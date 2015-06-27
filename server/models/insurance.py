# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Insurance(models.Model):
    insurer_name = models.CharField(max_length=256, blank=True)

    def __unicode__(self):
        return self.insurer_name
