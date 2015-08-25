# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from driver import Driver

class PaymentMethod(models.Model):
    driver = models.ForeignKey(Driver)
    gateway_name = models.CharField(max_length=16)
    gateway_token = models.CharField(max_length=256)
    suffix = models.CharField(max_length=4)
    card_type = models.CharField(max_length=32)
    card_logo = models.CharField(max_length=256)
    expiration_date = models.DateField(null=True, blank=True, default=None)
    unique_number_identifier = models.CharField(max_length=32)

    def __unicode__(self):
        return '{} {} (pk{})'.format(self.card_type, self.suffix, self.pk)
