# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from server import models

most_recent_request_data = None

next_payment_response = None
make_payment_log = []

next_payment_method_response = None
add_payment_method_log = []

SUCCESS_CHALLENGE = 'success_challenge'
FAILURE_CHALLENGE = 'failure_challenge'


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
