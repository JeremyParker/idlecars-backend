# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from server import models


most_recent_request_data = None

next_payment_method_response = None

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

    driver.braintree_customer_id = '62358761'
    driver.save()

    return result


# store a queue of (status, error_message) tuples to override gateway responses
next_payment_response = []
def push_next_payment_response(status_error_tuple):
    next_payment_response.append(status_error_tuple)

def fake_payment_function(func):
    def decorated_function(*args, **kwargs):
        result = func(*args, **kwargs)
        global next_payment_response
        if next_payment_response:
            result.status, result.error_message = next_payment_response.pop()
        return result

    return decorated_function


@fake_payment_function
def pre_authorize(payment):
    payment.transaction_id = 'transaction id'
    payment.status = models.Payment.PRE_AUTHORIZED
    return payment


@fake_payment_function
def void(payment):
    payment.status = models.Payment.VOIDED
    return payment


@fake_payment_function
def settle(payment):
    payment.transaction_id = 'transaction id'
    payment.status = models.Payment.SETTLED
    return payment


@fake_payment_function
def escrow(payment):
    payment.transaction_id = 'transaction id'
    payment.status = models.Payment.HELD_IN_ESCROW
    return payment
