# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

import braintree

from django.conf import settings

from server import models


def configure_braintree():
    config = settings.BRAINTREE
    if isinstance(config["environment"], unicode):
        config["environment"] = getattr(braintree.Environment, config["environment"])
    braintree.Configuration.configure(**config)


def initialize_gateway(driver):
    configure_braintree()
    return {'client_token': braintree.ClientToken.generate(),}


def add_payment_method(driver, nonce):  # TODO: I don't think driver should be passed in. The ID should passed out.
    configure_braintree()

    customer_id = driver.braintree_customer_id
    if not customer_id:
        request = {
            'first_name': driver.first_name(),
            'last_name': driver.last_name(),
            'custom_fields': {
                'idlecars_customer_id': driver.id,
            }
        }
        response = braintree.Customer.create(request)
        success = response.is_success
        # record_in_history(models.PaymentGatewayHistory.OPERATION.NEW_CUSTOMER, customer, None, None, request, response, success)
        customer_id = response.customer.id
        driver.braintree_customer_id = customer_id
        driver.save()

    request = {
        "customer_id": customer_id,
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


def make_payment(payment, nonce):
    configure_braintree()

    request = {
        "amount": str(payment.amount),
        # "merchant_account_id": settings.BRAINTREE["merchant_id"],
        # "customer_id": payment.booking.driver.braintree_customer_id,
        "options": {
            "submit_for_settlement": True,
        },
    }

    if nonce:
        request['payment_method_nonce'] = nonce

    response = braintree.Transaction.sale(request)
    success = getattr(response, "is_success", False)

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
    transaction_token = None
    if hasattr(response, "transaction"):
        transaction_token = response.transaction.id
        if hasattr(response.transaction, "credit_card"):
            card = response.transaction.credit_card
            expiration_date = datetime.date(int(card["expiration_year"]), int(card["expiration_month"]), 1)

    if success:
        result = models.Payment.APPROVED
        error_message = ""
    else:
        result, error_message, suspicious_activity = parse_payment_error(response)
        # record.error = error_message
        # record.save()
        # TODO: if suspicious_activity: send an email

    return result, transaction_token, error_message, expiration_date
