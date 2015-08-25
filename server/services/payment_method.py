# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from server import payment_gateways
from server import models


def add_payment_method(driver, nonce):
    gateway = payment_gateways.get_gateway(settings.PAYMENT_GATEWAY_NAME)
    success, card_details = gateway.add_payment_method(driver, nonce)

    if success:
        driver.paymentmethod_set.all().delete() # TDOO: keep all payment methods and mark latest 'default'
        token, suffix, card_type, card_logo, expiration_date, unique_number_identifier = card_details
        payment_method = models.PaymentMethod.objects.create(
            driver=driver,
            gateway_name=settings.PAYMENT_GATEWAY_NAME,
            gateway_token=nonce,
            suffix=suffix,
            card_type=card_type,
            card_logo=card_logo,
            expiration_date=expiration_date,
            unique_number_identifier=unique_number_identifier,
        )

    return driver
