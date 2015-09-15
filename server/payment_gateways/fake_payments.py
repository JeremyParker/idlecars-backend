# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from server import models


most_recent_request_data = None

next_payment_method_response = None
add_payment_method_log = []


def confirm_endpoint(challenge):
    # TODO - for testing, respond to success/failure input
    return {'success': True}


def link_bank_account(braintree_params):
    global most_recent_request_data
    most_recent_request_data = braintree_params
    if not 'tos_accepted' in braintree_params.keys() or not braintree_params['tos_accepted']:
        return (
            False,
            '',  # merchant_account_id
            ['tos_accepted'],
            ['Terms Of Service needs to be accepted. Applicant tos_accepted required.'],
        )
    return True, 'test_submerchant_account_id', [], []


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


def pre_authorize(payment):
    payment.transaction_id = 'transaction id'
    payment.status = models.Payment.PRE_AUTHORIZED
    return payment


def void(payment):
    payment.status = models.Payment.VOIDED
    return payment


def settle(payment):
    payment.transaction_id = 'transaction id'
    payment.status = models.Payment.SETTLED
    return payment


def escrow(payment):
    payment.transaction_id = 'transaction id'
    payment.status = models.Payment.HELD_IN_ESCROW
    return payment
