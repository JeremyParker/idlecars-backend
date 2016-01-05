# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core import exceptions

from idlecars import model_helpers, fields
from server.models import Owner

class OnboardingOwner(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    published_date = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=40, unique=True)
    name = model_helpers.StrippedCharField(max_length=30, blank=True)

    def save(self, *args, **kwargs):
        self.phone_number = fields.parse_phone_number(self.phone_number)
        super(OnboardingOwner, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.phone_number
