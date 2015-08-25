# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from server import payment_gateways
from server import models


def add_payment_method(driver, nonce):
    gateway = payment_gateways.get_gateway(settings.PAYMENT_GATEWAY_NAME)
    success, card_details = gateway.add_payment_method(driver, nonce)

    # create a payment method object

    return driver
