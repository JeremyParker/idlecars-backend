# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from server import models


next_payment_response = None
make_payment_log = []

next_payment_method_response = None
add_payment_method_log = []


def add_payment_method(driver, nonce):
    global next_payment_method_response
    add_payment_method_log.append((driver, nonce,))

    if next_payment_method_response is None:
        result = True, (
            'some-token',
            '1234',
            'Visa',
            'https://assets.braintreegateway.com/payment_method_logo/visa.png?environment=sandbox',
            datetime.date(2016, 8, 30),
            '',
        )
    else:
        result = next_payment_method_response
    next_payment_method_response = None
    return result


def make_payment(payment, escrow=False, nonce=None, token=None):
    global next_payment_response
    make_payment_log.append(payment)

    if next_payment_response:
        result = next_payment_response
    elif nonce or token:
        result = (models.Payment.APPROVED, 'test_transaction_id', '',)
    else:
        result = (models.Payment.DECLINED, 'test_transaction_id', 'No funds available',)
    next_payment_response = None
    return result


def reset():
    global make_payment_log
    make_payment_log = []
