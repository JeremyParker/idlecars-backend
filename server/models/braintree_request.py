# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from payment import Payment
from payment_method import PaymentMethod

class BraintreeRequest(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    payment_method = models.ForeignKey(PaymentMethod, null=True)
    payment = models.ForeignKey(Payment, null=True)
    endpoint = models.CharField(max_length=64)
    request = models.TextField(blank=True)
    response = models.TextField(blank=True)
