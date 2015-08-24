# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree
from django.conf import settings


def configure_braintree():
    config = settings.BRAINTREE
    if isinstance(config["environment"], unicode):
        config["environment"] = getattr(braintree.Environment, config["environment"])
    braintree.Configuration.configure(**config)


def initialize_gateway(driver):
    configure_braintree()
    return {'client_token': braintree.ClientToken.generate(),}


def add_card(desc, driver):
    """ add a credit card
    may modify the driver instance
    """
    configure_braintree()

    customer_token = driver.braintree_token
    if not customer_token:
        request = {
            "custom_fields": {
                "idlecars_customer_id": customer.id
            }
        }
        response = braintree.Customer.create(request)
        success = True
        # record_in_history(models.PaymentGatewayHistory.OPERATION.NEW_CUSTOMER, customer, None, None, request, response, success)
        customer_token = response.customer.id
        driver.braintree_token = customer_token
        driver.save()

    request = {
        "customer_id": customer_token,
        "payment_method_nonce": desc.payment_method_nonce,
        "options": {
            "verification_merchant_account_id": desc.currency.braintree_merchant_account,
            "make_default": True,
        }
    }
    if desc.postal_code is not None:
        request['billing_address'] = {
            "postal_code": desc.postal_code,
            "country_code_alpha2": "US",
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
            exp = datetime.date(int(payment_method.expiration_year), int(payment_method.expiration_month), 1)
            unique_number_identifier = payment_method.unique_number_identifier

        return True, (card_token, card_suffix, card_type, record, exp, unique_number_identifier)
    else:
        error_message, error_fields, suspicious_activity = parse_card_error(response)
        error = error_message, error_fields
        record.error = str(error)
        record.save()

        if suspicious_activity:
            send_suspicious_activity_email(customer, device, None, record)

        return False, error


def parse_payment_error(response):
    status = response.transaction.status
    if status == "gateway_rejected":
        known_gateway_errors = {
            # third value is 'suspicious activity' flag
            "duplicate": (PAYMENT_DECLINED, SPEED_LIMIT_MSG, False),
            "fraud": (PAYMENT_DECLINED, PAYMENT_FRAUD_MSG, True),
        }
        gateway_error = response.transaction.gateway_rejection_reason
        if gateway_error in known_gateway_errors:
            return known_gateway_errors[gateway_error]
        else:
            raise Exception("Unknown braintree gateway error " + gateway_error)
    elif status in {"processor_declined", "failed"}:
        known_processor_errors = {
            # third value is 'suspicious activity' flag
            "2000": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, False),  # Do Not Honor
            "2001": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, False),  # Insufficient Funds
            "2003": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, False),  # Cardholder's Activity Limit Exceeded
            "2004": (PAYMENT_DECLINED, EXPIRED_PAYMENT_DECLINED_MSG, False),  # Expired Card
            "2005": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, False),  # Invalid Credit Card Number
            "2011": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, False),  # Voice Authorization Required
            "2015": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, False),  # Transaction Not Allowed
            "2024": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, False),  # Card Type Not Enabled
            "2038": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, False),  # Processor Declined
            "2046": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, False),  # Declined
            "2047": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, True),  # Call Issuer. Pick Up Card. (the bank wants the card back...)
            "2053": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, True),  # Card reported as lost or stolen
            "2057": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, True),  # Issuer or Cardholder has put a restriction on the card
            "2074": (PAYMENT_DECLINED, BAD_PAYPAL_DETAILS_MSG, False),  # Funding Instrument In The PayPal Account Was Declined By The Processor Or Bank, Or It Can't Be Used For This Payment.
            "2076": (PAYMENT_DECLINED, PAYMENT_DECLINED_MSG, False),  # Payer Cannot Pay For This Transaction With PayPal
            "3000": (PAYMENT_DECLINED, UNKNOWN_ERROR_MSG, False),  # Processor Network Unavailable - Try Again
        }
        processor_error = response.transaction.processor_response_code
        if processor_error in known_processor_errors:
            return known_processor_errors[processor_error]
        else:
            raise Exception("Unknown braintree processor error " + processor_error)
    else:
        raise Exception("Unknown braintree status " + status)


def make_payment(payment, nonce):
    configure_braintree()

    request = {
        "amount": str(payment.amount),
        "merchant_account_id": settings.BRAINTREE["merchant_id"],
        "customer_id": payment.booking.driver.braintree_token,
        "options": {
            "submit_for_settlement": True,
        },
        "custom_fields": {
            "idlecars_payment_id": payment.id,
        },
    }

    if nonce:
        request['payment_method_nonce'] = nonce
    else:
        request["payment_method_token"] = payment.credit_card.gateway_token

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

    # expiry_date = None
    # transaction_token = None
    # if hasattr(response, "transaction"):
    #     transaction_token = response.transaction.id
    #     if hasattr(response.transaction, "credit_card"):
    #         card = response.transaction.credit_card
    #         expiration_date = datetime.date(int(card["expiration_year"]), int(card["expiration_month"]), 1)

    if success:
        result = APPROVED
        error_message = ""
    else:
        result, error_message, suspicious_activity = parse_payment_error(response)
        # record.error = error_message
        # record.save()
        # TODO: if suspicious_activity: send an email

    return result, transaction_token, error_message, expiration_date
