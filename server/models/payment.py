# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from server.models import Booking, PaymentMethod

class Payment(models.Model):
    PENDING = 0
    APPROVED = 1
    DECLINED = 2
    REJECTED = 3
    STATUS = (
        (PENDING, 'Pending gateway response'),
        (APPROVED, 'Payment approved'),
        (DECLINED, 'Payment declined'),
        (REJECTED, 'Card rejected'),
    )
    booking = models.ForeignKey(Booking)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.ForeignKey(PaymentMethod, null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=PENDING)
    error_message = models.CharField(max_length=256)
    transaction_id = models.CharField(max_length=32)

    def __unicode__(self):
        return '{} from {}'.format(self.amount, self.booking.driver) # self.credit_card)

    def is_paid(self):
        return self.status == Payment.APPROVED
