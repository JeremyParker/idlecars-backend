# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
import braintree

from django.conf import settings

from server import models


configured = False

def _configure_braintree():
    global configured
    if not configured:
        config = settings.BRAINTREE
        if isinstance(config["environment"], unicode):
            config["environment"] = getattr(braintree.Environment, config["environment"])
        braintree.Configuration.configure(**config)
    configured = True


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


def _transaction_request(payment):
    payment_method = payment.booking.driver.paymentmethod_set.last()
    return {
        'payment_method_token': payment_method.gateway_token,
        'amount': str(payment.amount),
        'customer_id': payment.booking.driver.braintree_customer_id,
        'merchant_account_id': payment.booking.car.owner.merchant_id,
        'service_fee_amount': payment.service_fee,
    }


def pre_authorize(payment):
    assert not payment.transaction_id
    _configure_braintree()
    request = _transaction_request(payment)
    request.update({ 'options': { 'submit_for_settlement': False }})

    response = braintree.Transaction.sale(request)
    if getattr(response, 'is_success', False):
        if response.transaction.status != 'authorized':
            # TODO: logging system
            print 'WARNING: an authorized transaction state was not "authorized"'
        payment.status = models.Payment.PRE_AUTHORIZED
        payment.error_message = ""
    else:
        payment.status, payment.error_message = parse_payment_error(response)  # TODO

    if hasattr(response, "transaction"):
        payment.transaction_id = response.transaction.id

    return payment


def void(payment):
    assert payment.transaction_id
    assert payment.status is models.Payment.PRE_AUTHORIZED
    _configure_braintree()

    response = braintree.Transaction.void(payment.transaction_id)
    if getattr(response, 'is_success', False):
        if response.transaction.status != 'voided':
            # TODO: logging system
            print 'WARNING: A voided transaction state was not "voided"'
        payment.status = models.Payment.VOIDED
        payment.error_message = ""
    else:
        payment.status, payment.error_message = parse_payment_error(response)  # TODO
    return payment


def settle(payment):
    _configure_braintree()
    if payment.transaction_id:
        response = braintree.Transaction.submit_for_settlement(payment.transaction_id)
    else:
        request = _transaction_request(payment)
        request.update({ 'options': { 'submit_for_settlement': True }})
        response = braintree.Transaction.sale(request)

    if getattr(response, 'is_success', False):
        if response.transaction.status not in [
            'settlement_pending',
            'settlement_confirmed',
            'submitted_for_settlement',
        ]:
            # TODO: logging system
            print 'WARNING: A settled transaction state had a non-settled status'

        payment.status = models.Payment.SETTLED
        payment.error_message = ""
    else:
        payment.status, payment.error_message = parse_payment_error(response)  # TODO
    return payment


def escrow(payment):
    _configure_braintree()
    if payment.transaction_id:
        response = braintree.Transaction.hold_in_escrow(payment.transaction_id)
    else:
        request = _transaction_request(payment)
        request.update({
            'options': {
                'submit_for_settlement': True,
                'hold_in_escrow': True,
            }
        })
        response = braintree.Transaction.sale(request)

    if getattr(response, 'is_success', False):
        if response.transaction.escrow_status not in [
            'hold_pending',
            'held',
        ]:
            # TODO: logging system
            print 'WARNING: A transaction in escrow had a non-escrow status: {}'.format(
                response.transaction.escrow_status
            )
        payment.status = models.Payment.HELD_IN_ESCROW
        payment.error_message = ''
    else:
        payment.status, payment.error_message = parse_payment_error(response)  # TODO
    return payment
