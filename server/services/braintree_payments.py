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


def make_payment(amount, nonce):
    configure_braintree()
    request = {
        'amount': str(amount),
        'payment_method_nonce': nonce,
    }
    response = braintree.Transaction.sale(request)
    success = getattr(response, "is_success", False)
    return success
