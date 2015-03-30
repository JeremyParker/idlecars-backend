# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from idlecars import model_helpers

class FleetPartner(models.Model):
    name = models.CharField(max_length=256)
    contact = models.CharField(max_length=256, blank=True)
    phone_number = models.CharField(max_length=256, blank=True, help_text="Comma separated", db_column='phone')
    email = models.CharField(max_length=256, blank=True, help_text="Comma separated")

    def __unicode__(self):
        return self.name


class Driver(models.Model):
    first_name = model_helpers.StrippedCharField(max_length=30, blank=True)
    last_name = model_helpers.StrippedCharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=40, blank=True)
    email = models.CharField(blank=True, max_length=128, null=True, unique=True)
    email_verified = models.DateTimeField(null=True, blank=True)

    def full_name(self):
        return u"{first_name} {last_name}".format(first_name=self.first_name, last_name=self.last_name).title()

    def __unicode__(self):
        if self.email:
            return "{name} ({email})".format(name=self.full_name(), email=self.email)
        else:
            return "{name} ({pk})".format(name=self.full_name(), pk=self.pk)
