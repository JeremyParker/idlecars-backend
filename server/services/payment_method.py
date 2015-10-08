# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from server import payment_gateways
from server import models


class PaymentMethoError(Exception):
    pass


def add_payment_method(driver, nonce):
    gateway = payment_gateways.get_gateway(settings.PAYMENT_GATEWAY_NAME)
    success, details = gateway.add_payment_method(driver, nonce)

    if success:
        driver.paymentmethod_set.all().delete() # TDOO: keep all payment methods and mark latest 'default'
        token, suffix, card_type, card_logo, expiration_date, unique_number_identifier = details
        payment_method = models.PaymentMethod.objects.create(
            driver=driver,
            gateway_token=token,
            suffix=suffix,
            card_type=card_type,
            card_logo=card_logo,
            expiration_date=expiration_date,
            unique_number_identifier=unique_number_identifier,
        )
        return driver

    raise PaymentMethoError(details)  # Not successful? Raise an error.
