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
        (PENDING, 'Unpaid'),
        (PRE_AUTHORIZED, 'Pre-authorized'),
        (SETTLED, 'Paid'),
        (HELD_IN_ESCROW, 'In escrow'),
        (REFUNDED, 'Refunded'),
        (VOIDED, 'Canceled'),
        (DECLINED, 'Declined'),
        (REJECTED, 'Rejected'),
    )

    created_time = models.DateTimeField(auto_now_add=True)
    booking = models.ForeignKey(Booking)

    # define the period they're paying for (None if it's a deposit)
    invoice_start_time = models.DateTimeField(blank=True, null=True)
    invoice_end_time = models.DateTimeField(blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2) # total amount charged in cash
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # service fee that was actually deducted through Braintree. The amount due is in the booking.
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    idlecars_supplement = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    idlecars_transaction_id = models.CharField(max_length=32, blank=True)

    payment_method = models.ForeignKey(PaymentMethod, null=True, blank=True)
    status = models.IntegerField(choices=STATUS, default=PENDING)
    error_message = models.CharField(max_length=256)
    transaction_id = models.CharField(max_length=32, blank=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return '{} from {}'.format(self.amount, self.booking.driver)

    def invoice_description(self):
        if self.invoice_start_time and self.invoice_end_time:
            return 'Rent {} to {}'.format(
                self.invoice_start_time.strftime("%b %d, %Y"),
                self.invoice_end_time.strftime("%b %d, %Y"),
            )
        return 'Deposit'

    def status_string(self):
        return dict(Payment.STATUS)[self.status]
