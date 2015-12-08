# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.db import models
from django.conf import settings


class Customer(models.Model):
    '''
    Customer represents an owner or a driver, and has fields that are common to both. If we
    could change auth.User we would add these fields there, but this is simpler.
    '''
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    # the code I used when I signed up
    invitor_code = models.ForeignKey("CreditCode", null=True, blank=True, verbose_name="Invited by")
    invitor_credited = models.BooleanField(default=False)

    # the code I can give out to others
    invite_code = models.OneToOneField("CreditCode", null=True, blank=True, unique=True, related_name="invitor")

    # how much app credit I have.
    app_credit = models.DecimalField(max_digits=10, decimal_places=2, default=decimal.Decimal('0.00'))
