# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.db import models

from server.models import Booking, PaymentMethod

class Payment(models.Model):
    PENDING = 0
    PRE_AUTHORIZED = 1
    SETTLED = 2
    HELD_IN_ESCROW = 3
    REFUNDED = 4
    VOIDED = 5
    DECLINED = 6
    REJECTED = 7

    STATUS = (
        (PENDING, 'Pending'),
        (PRE_AUTHORIZED, 'Pre-authorized'),
        (SETTLED, 'Settled'),
        (HELD_IN_ESCROW, 'In Escrow'),
        (REFUNDED, 'Payment refunded'),
        (VOIDED, 'Voided'),
        (DECLINED, 'Payment declined'),
        (REJECTED, 'Card rejected'),
    )

    created_time = models.DateTimeField(auto_now_add=True)
    booking = models.ForeignKey(Booking)
    week_ending = models.DateTimeField(blank=True, null=True)  # end of the week they're paying for

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    payment_method = models.ForeignKey(PaymentMethod, null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=PENDING)
    error_message = models.CharField(max_length=256)
    transaction_id = models.CharField(max_length=32, blank=True)

    def __unicode__(self):
        return '{} from {}'.format(self.amount, self.booking.driver)

    def is_paid(self):
        return self.status == Payment.SETTLED or self.status == HELD_IN_ESCROW
