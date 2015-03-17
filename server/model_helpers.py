# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class StrippedCharField(models.CharField):
    def get_prep_value(self, value):
        val = super(StrippedCharField, self).get_prep_value(value)
        if val is not None:
            return val.strip()
        else:
            return None
