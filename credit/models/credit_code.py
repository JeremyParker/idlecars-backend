# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class CreditCode(models.Model):
    description = models.CharField(max_length=256, blank=True, help_text="What promotion was this for?")

    credit_code = models.CharField(max_length=16, unique=True)
    created_time = models.DateTimeField(auto_now_add=True, blank=True)
    expiry_time = models.DateTimeField(blank=True, null=True)
    redeem_count = models.IntegerField(default=0, help_text="Number of users who have used this code")

    credit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    invitor_credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __unicode__(self):
        return self.description or self.credit_code
