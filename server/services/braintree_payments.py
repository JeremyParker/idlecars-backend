# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree
from django.conf import settings


def configure_braintree():
    config = settings.BRAINTREE
    if isinstance(config["environment"], unicode):
        config["environment"] = getattr(braintree.Environment, config["environment"])
    braintree.Configuration.configure(**config)


def initialize_gateway(customer):
    configure_braintree()

    return {
        'client_token': braintree.ClientToken.generate(),
    }
