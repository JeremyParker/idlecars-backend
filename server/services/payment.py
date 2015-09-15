# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from server import payment_gateways
from server import models


def create_payment(booking, amount):
    payment_method = booking.driver.paymentmethod_set.last() # TODO: store 'em all & make latest default
    assert payment_method.driver == booking.driver

    payment = models.Payment.objects.create(
        booking=booking,
        amount=amount,
        payment_method=payment_method,
    )
    return payment


def _execute(function, payment):
    '''
    Execute a payment gatway method on the active gateway. This accomplishes redirection
    between Braintree or Fake (or another gateway we might switch to in the future.)
    '''
    gateway = payment_gateways.get_gateway(settings.PAYMENT_GATEWAY_NAME)
    func = getattr(gateway, function)
    payment = func(payment)
    payment.save()
    return payment


def pre_authorize(payment):
    return _execute('pre_authorize', payment)


def settle(payment):
    return _execute('settle', payment)


def void(payment):
    return _execute('void', payment)


def escrow(payment):
    return _execute('escrow', payment)
