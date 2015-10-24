# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from server import payment_gateways
from server import models


class PaymentMethoError(Exception):
    pass


def add_payment_method(driver, nonce):
    payment_method = models.PaymentMethod.objects.create(
        driver=driver,
    )
    gateway = payment_gateways.get_gateway(settings.PAYMENT_GATEWAY_NAME)
    success, details = gateway.add_payment_method(payment_method, nonce)

    if success:
        token, suffix, card_type, card_logo, expiration_date, unique_number_identifier = details
        payment_method.gateway_token = token
        payment_method.suffix = suffix
        payment_method.card_type = card_type
        payment_method.card_logo = card_logo
        payment_method.expiration_date = expiration_date
        payment_method.unique_number_identifier = unique_number_identifier
        payment_method.save()
    else:
        raise PaymentMethoError(details)  # Not successful? Raise an error.
