# -*- encoding:utf-8 -*-
from __future__ import unicode_literals


def get_gateway(gateway_name):
    import braintree_payments
    import fake_payments

    gateways = {
        'braintree': braintree_payments,
        'fake': fake_payments,
    }
    return gateways[gateway_name]
