# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import test_braintree_params

def get_gateway(gateway_name):
    import braintree_payments
    import fake_payments

    gateways = {
        'braintree': braintree_payments,
        'fake': fake_payments,
    }
    return gateways[gateway_name]
