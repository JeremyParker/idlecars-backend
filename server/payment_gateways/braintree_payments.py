# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
import braintree

from django.conf import settings

from server import models


UNABLE_TO_ADD_DRIVER = 'Sorry, we couldn\'t add you to our system. We\'ll look into the problem and get back to you.'
EXPIRED_CARD_MSG = 'Sorry, it looks like your credit card has expired. Let\'s try another one'
UNSUPPORTED_PAYMENT_METHOD = 'Sorry, we\'re not accepting that form of payment right now. Try a credit card.'
PAYMENT_DECLINED_MSG = 'Sorry, your payment was declined. Please try another credit card.'
NETWORK_DOWN_MSG = 'Sorry, something went wrong with your payment. Please try again soon.'
SPEED_LIMIT_MSG = 'Sorry that didn\'t work. Please wait a minute before using this card again.'
GENERIC_MSG = 'Sorry that didn\'t work. The payment processor says "{}". Please call Idlecars at ' + settings.IDLECARS_PHONE_NUMBER + ' for help.'

configured = False

def _configure_braintree():
    global configured
    if not configured:
        config = settings.BRAINTREE
        if isinstance(config['environment'], unicode) or isinstance(config['environment'], str):
            config['environment'] = getattr(braintree.Environment, config['environment'])
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

        if success:
            driver.braintree_customer_id = response.customer.id
            driver.save()
            return driver, None
        else:
            return driver, UNABLE_TO_ADD_DRIVER

def _parse_card_info(payment_method):
    '''
    Returns a tuple of token, suffix, card_type, logo, expiration date, braintree_unique_number
    '''
    card_token = payment_method.token
    card_suffix = payment_method.last_4
    card_type = payment_method.card_type
    card_logo = payment_method.image_url
    exp = datetime.date(int(payment_method.expiration_year), int(payment_method.expiration_month), 1)
    unique_number_identifier = payment_method.unique_number_identifier
    return card_token, card_suffix, card_type, card_logo, exp, unique_number_identifier


def _parse_error(response):
    message = PAYMENT_DECLINED_MSG
    details = ''
    try:
        if response.transaction:
            details = unicode(response.transaction.__dict__)
            status = response.transaction.status
            if status == 'gateway_rejected':
                error = response.transaction.gateway_rejection_reason
                gateway_errors = {
                    'duplicate': SPEED_LIMIT_MSG,
                    'fraud': PAYMENT_DECLINED_MSG,
                }
                if error in gateway_errors:
                    message = gateway_errors[error]
            elif status in {'processor_declined', 'failed'}:
                processor_errors = {
                    '2000': PAYMENT_DECLINED_MSG,   # Do Not Honor
                    '2001': PAYMENT_DECLINED_MSG,   # Insufficient Funds
                    '2003': PAYMENT_DECLINED_MSG,   # Cardholder's Activity Limit Exceeded
                    '2004': EXPIRED_CARD_MSG,       # Expired Card
                    '2005': PAYMENT_DECLINED_MSG,   # Invalid Credit Card Number
                    '2011': PAYMENT_DECLINED_MSG,   # Voice Authorization Required
                    '2015': PAYMENT_DECLINED_MSG,   # Transaction Not Allowed
                    '2024': PAYMENT_DECLINED_MSG,   # Card Type Not Enabled
                    '2038': PAYMENT_DECLINED_MSG,   # Processor Declined
                    '2046': PAYMENT_DECLINED_MSG,   # Declined
                    '2047': PAYMENT_DECLINED_MSG,   # Call Issuer. Pick Up Card.
                    '2053': PAYMENT_DECLINED_MSG,   # Card reported as lost or stolen
                    '2057': PAYMENT_DECLINED_MSG,   # Issuer or Cardholder has put a restriction on the card
                    '3000': NETWORK_DOWN_MSG,       # Processor Network Unavailable - Try Again
                }
                processor_error = response.transaction.processor_response_code
                if processor_error in processor_errors:
                    message = processor_errors[processor_error]
                else:
                    msg = response.transaction.processor_response_code.processor_response_text
                    message = GENERIC_MSG.format(msg)
        else:
            details = response.errors.errors.data
            message = NETWORK_DOWN_MSG
    except Exception:
        message = NETWORK_DOWN_MSG

    return message, details


def initialize_gateway():
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
    success = getattr(response, 'is_success', False)
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


def add_payment_method(driver, nonce):  # TODO: I don't think driver should be passed in. The ID should passed in/out.
    '''
    Returns a bool, info pair. Bool = success/failure. The info should be either
    - card info tuple or
    - the error message string
    '''
    _configure_braintree()

    if not driver.braintree_customer_id:
        driver, error = _add_customer(driver)
        if not driver.braintree_customer_id:
            return False, driver, error

    request = {
        'customer_id': driver.braintree_customer_id,
        'payment_method_nonce': nonce,
        'options': {
            'make_default': True,
        }
    }
    response = braintree.PaymentMethod.create(request)
    success = getattr(response, 'is_success', False)
    if success:
        payment_method = response.payment_method
        if payment_method.is_expired:
            return False, driver, EXPIRED_CARD_MSG

        if isinstance(payment_method, braintree.CreditCard):
            card_info = _parse_card_info(payment_method)
            return True, driver, card_info
    else:
        message, _ = _parse_error(response)  # TODO - log the details somehow
        return False, driver, message


def _transaction_request(payment):
    return {
        'payment_method_token': payment.payment_method.gateway_token,
        'amount': str(payment.amount),
        'customer_id': payment.booking.driver.braintree_customer_id,
        'merchant_account_id': payment.booking.car.owner.merchant_id,
        'service_fee_amount': payment.service_fee,
    }


def pre_authorize(payment):
    assert not payment.transaction_id

    if not payment.amount:
        payment.status = models.Payment.PRE_AUTHORIZED
        payment.error_message = ''
        return payment

    _configure_braintree()
    request = _transaction_request(payment)
    request.update({ 'options': { 'submit_for_settlement': False }})
    response = braintree.Transaction.sale(request)
    if hasattr(response, 'transaction') and response.transaction:
        payment.transaction_id = response.transaction.id

    if getattr(response, 'is_success', False):
        if response.transaction.status != 'authorized':
            print 'WARNING: authorized transaction {} state was not "authorized"'.format(
                payment.transaction_id,
            )
        payment.status = models.Payment.PRE_AUTHORIZED
        payment.error_message = ''
    else:
        payment.status = models.Payment.DECLINED
        payment.error_message, payment.notes = _parse_error(response)

    return payment


def void(payment):
    assert payment.status is models.Payment.PRE_AUTHORIZED

    if not payment.amount:
        payment.status = models.Payment.VOIDED
        payment.error_message = ''
        return payment

    assert payment.transaction_id
    _configure_braintree()

    response = braintree.Transaction.void(payment.transaction_id)
    if getattr(response, 'is_success', False):
        if response.transaction.status != 'voided':
            # TODO: logging system
            print 'WARNING: voided transaction {} status != "voided"'.format(payment.transaction_id)
        payment.status = models.Payment.VOIDED
        payment.error_message = ''
    else:
        payment.status = models.Payment.DECLINED
        payment.error_message, payment.notes = _parse_error(response)
    return payment


def settle(payment):
    if not payment.amount:
        payment.status = models.Payment.SETTLED
        payment.error_message = ''
        return payment

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
            print 'WARNING: settled transaction {} had a non-settled status'.format(
                payment.transaction_id,
            )

        payment.status = models.Payment.SETTLED
        payment.error_message = ''
    else:
        payment.status = models.Payment.DECLINED
        payment.error_message, payment.notes = _parse_error(response)
    return payment


def escrow(payment):
    if not payment.amount:
        payment.status = models.Payment.HELD_IN_ESCROW
        payment.error_message = ''
        return payment

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
        if hasattr(response, 'transaction') and response.transaction:
            payment.transaction_id = response.transaction.id

    if getattr(response, 'is_success', False):
        if response.transaction.escrow_status not in [
            'hold_pending',
            'held',
        ]:
            # TODO: logging system
            print 'WARNING: transaction {} in escrow had a non-escrow status: {}'.format(
                payment.transaction_id,
                response.transaction.escrow_status,
            )
        payment.status = models.Payment.HELD_IN_ESCROW
        payment.error_message = ''
    else:
        payment.status = models.Payment.DECLINED
        payment.error_message, payment.notes = _parse_error(response)
    return payment


def refund(payment):
    _configure_braintree()
    if payment.transaction_id:
        response = braintree.Transaction.refund(payment.transaction_id)
        if getattr(response, 'is_success', False):
            payment.status = models.Payment.REFUNDED
            payment.error_message = ''
        else:
            payment.error_message, payment.notes = _parse_error(response)
    return payment
