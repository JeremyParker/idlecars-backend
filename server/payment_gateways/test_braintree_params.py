# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from braintree.test.nonces import Nonces

'''
Api ==> Services ==> PaymentsGateway ==> Braintree Sandbox

This file contains test input values to be used in tests against fake_payments.
It also contains the expected values that we should be sending to Braintree as
part of those operations. The expected values that we send to Braintree can then
be tested in an integration test to make sure they work against the Sandbox.
'''

VALID_ROUTING_NUMBER = '071101307'
VALID_VISA_NONCE = Nonces.TransactableVisa
INVALID_PAYMENT_METHOD_NONCE = Nonces.Consumed


business_data = {
    'from_client': {
        'business': {
            'legal_name': 'Craig\'s Awesome Business',
            'tax_id': '121234567',
        },
        'funding': {
            'account_number': '1234567890',
            'routing_number': '071101307',
        },
        'individual': {
            'address': {
                'locality': 'New York',
                'postal_code': '10014',
                'region': 'NY',
                'street_address': '95 Morton St',
            },
            'date_of_birth': '19880408',
            'email': 'email@buddy.com',
            'first_name': 'Mike',
            'last_name': 'Malone',
            'phone_number': '(123) 123-9987',
        },
        'tos_accepted': True,
     },
    'to_braintree': {
        'business': {
            'legal_name': 'Craig\'s Awesome Business',
            'tax_id': '121234567',
        },
        'funding': {
            'account_number': '1234567890',
            'routing_number': '071101307',
        },
        'individual': {
            'address': {
                'locality': 'New York',
                'postal_code': '10014',
                'region': 'NY',
                'street_address': '95 Morton St',
            },
            'date_of_birth': '19880408',
            'email': 'email@buddy.com',
            'first_name': 'Mike',
            'last_name': 'Malone',
            'phone': '(123) 123-9987',
        },
        "tos_accepted": True,
    }
}


# sample of the data that an individual submits through the client
individual_data = {
    'from_client': {
        'funding': {
            'account_number': '1234567890',
            'routing_number': '071101307'
        },
        'individual': {
            'address': {
                'locality': 'Brooklyn',
                'postal_code': '11221',
                'region': 'NY',
                'street_address': '276 Kosciuszko St'
            },
            'date_of_birth': '19890508',
            'email': 'awesome@perfect.org',
            'first_name': 'Mike',
            'last_name': 'Malone',
            'phone_number': '(123) 123-9987',
        },
        'tos_accepted': True
    },
    'to_braintree': {
        'funding': {
            'account_number': "1234567890",
            'routing_number': "071101307",
        },
        'individual': {
            'address': {
                'locality': 'Brooklyn',
                'postal_code': '11221',
                'region': 'NY',
                'street_address': '276 Kosciuszko St'
            },
            'date_of_birth': '19890508',
            'email': 'awesome@perfect.org',
            'first_name': 'Mike',
            'last_name': 'Malone',
            'phone': '(123) 123-9987',
        },
        "tos_accepted": True,
    }
}
