# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from random import randint
from decimal import Decimal

from idlecars.factory_helpers import Factory

from server import models


class Payment(Factory):
    class Meta:
        model = 'server.Payment'
    amount = Decimal('9.{}'.format(randint(1, 99)))


class PreAuthorizedPayment(Payment):
    transaction_id = 'some_transaction_id'
    status = models.Payment.PRE_AUTHORIZED


class HeldInEscrowPayment(Payment):
    status = models.Payment.HELD_IN_ESCROW


class SettledPayment(PreAuthorizedPayment):
    status = models.Payment.SETTLED


class FailedPayment(Payment):
    ''' Requires a Booking passed in the create() function '''
    transaction_id = 'some_transaction_id'
    status = models.Payment.DECLINED
    error_message = 'This transaction was declined for some reason.'

class RefundedPayment(PreAuthorizedPayment):
    status = models.Payment.VOIDED
