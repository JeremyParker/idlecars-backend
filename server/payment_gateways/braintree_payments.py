# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
import braintree

from django.conf import settings

from server import models


def _configure_braintree():
    config = settings.BRAINTREE
    if isinstance(config["environment"], unicode) or isinstance(config["environment"], str):
        config["environment"] = getattr(braintree.Environment, config["environment"])
    braintree.Configuration.configure(**config)


def _add_customer(driver):
        request = {
            'first_name': driver.first_name(),
            'last_name': driver.last_name(),
            'custom_fields': {
                'idlecars_customer_id': driver.id,
            }
        }
        response = braintree.Customer.create(request)
        success = getattr(response, 'is_success', False)

        customer_id = response.customer.id
        driver.braintree_customer_id = customer_id
        driver.save()

        return driver


def initialize_gateway(driver):
    _configure_braintree()
    return {'client_token': braintree.ClientToken.generate(),}


def confirm_endpoint(challenge):
    _configure_braintree()
    return braintree.WebhookNotification.verify(challenge)


def parse_webhook_notification(bt_signature, bt_payload):
    _configure_braintree()
    return braintree.WebhookNotification.parse(bt_signature, bt_payload)


def link_bank_account(braintree_params):
    '''
    Returns success (bool), 'account_id', [error_fields], [error_messages]
    '''
    _configure_braintree()

    braintree_params['funding']['destination'] = braintree.MerchantAccount.FundingDestination.Bank
    braintree_params['master_merchant_account_id'] = settings.MASTER_MERCHANT_ACCOUNT_ID

    response = braintree.MerchantAccount.create(braintree_params)
    success = getattr(response, "is_success", False)
    if success:
        account = response.merchant_account.id if response.merchant_account else ''
        return success, account, [], []
    else:
        return (
            success,
            '',  # merchant_account_id
            [e.attribute for e in response.errors.deep_errors],
            [e.message for e in response.errors.deep_errors],
        )

def add_payment_method(driver, nonce):  # TODO: I don't think driver should be passed in. The ID should passed out.
    _configure_braintree()

    if not driver.braintree_customer_id:
        driver = _add_customer(driver)
        if not driver.braintree_customer_id:
            raise Exception('Unable to add a customer to Braintree.')

    request = {
        "customer_id": driver.braintree_customer_id,
        "payment_method_nonce": nonce,
        "options": {
            "make_default": True,
        }
    }

    response = braintree.PaymentMethod.create(request)
    success = getattr(response, "is_success", False)

    if success:
        payment_method = response.payment_method
        card_token = payment_method.token

        if isinstance(payment_method, braintree.CreditCard):
            if payment_method.is_expired:
                return False, (EXPIRED_CARD_MSG, ["expiry_date"])

            card_suffix = payment_method.last_4
            card_type = payment_method.card_type
            card_logo = payment_method.image_url
            exp = datetime.date(int(payment_method.expiration_year), int(payment_method.expiration_month), 1)
            unique_number_identifier = payment_method.unique_number_identifier

        return True, (card_token, card_suffix, card_type, card_logo, exp, unique_number_identifier)
    else:
        error_message, error_fields, suspicious_activity = parse_card_error(response)
        error = error_message, error_fields
        return False, error


def make_payment(payment, escrow=False, nonce=None, token=None):
    assert nonce or token
    _configure_braintree()

    request = {
        'amount': str(payment.amount),
        'customer_id': payment.booking.driver.braintree_customer_id,
        'options': {
            'submit_for_settlement': True,
            # 'hold_in_escrow': escrow,
        },
    }

    if nonce:
        request['payment_method_nonce'] = nonce
    elif token:
        request['payment_method_token'] = token

    response = braintree.Transaction.sale(request)
    success = getattr(response, 'is_success', False)

    transaction_id = None
    if hasattr(response, "transaction"):
        transaction_id = response.transaction.id

    if success:
        result = models.Payment.APPROVED
        error_message = ""
    else:
        result, error_message, suspicious_activity = parse_payment_error(response)

    return result, transaction_id, error_message
