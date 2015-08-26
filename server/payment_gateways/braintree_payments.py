# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
import braintree

from django.conf import settings

from server import models


def _configure_braintree():
    config = settings.BRAINTREE
    if isinstance(config["environment"], unicode):
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
        # record_in_history(models.PaymentGatewayHistory.OPERATION.NEW_CUSTOMER, customer, None, None, request, response, success)

        customer_id = response.customer.id
        driver.braintree_customer_id = customer_id
        driver.save()

        return driver


def initialize_gateway(driver):
    _configure_braintree()
    return {'client_token': braintree.ClientToken.generate(),}


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

    # record = record_in_history(
    #     models.PaymentGatewayHistory.OPERATION.NEW_CARD,
    #     customer,
    #     None,  # card is filled in later
    #     None,
    #     device,
    #     request,
    #     response,
    #     success,
    # )

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
        # record.error = str(error)
        # record.save()

        # if suspicious_activity:
        #     send_suspicious_activity_email(customer, device, None, record)
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

    # record = record_in_history(
    #     models.PaymentGatewayHistory.OPERATION.PAYMENT,
    #     payment.booking.customer,
    #     payment.credit_card,
    #     payment,
    #     payment.booking.device,
    #     request,
    #     response,
    #     success,
    # )

    expiration_date = None
    transaction_id = None
    if hasattr(response, "transaction"):
        transaction_id = response.transaction.id

    if success:
        result = models.Payment.APPROVED
        error_message = ""
    else:
        result, error_message, suspicious_activity = parse_payment_error(response)
        # record.error = error_message
        # record.save()
        # TODO: if suspicious_activity: send an email

    return result, transaction_id, error_message, expiration_date
