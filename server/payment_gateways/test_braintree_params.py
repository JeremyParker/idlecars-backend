# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

'''
Api ==> Services ==> PaymentsGateway ==> Braintree Sandbox

This file contains test input values to be used in tests against fake_payments.
It also contains the expected values that we should be sending to Braintree as
part of those operations. The expected values that we send to Braintree can then
be tested in an integration test to make sure they work against the Sandbox.
'''


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
            # 'address': {
            #     'street_address': "111 Main St",
            #     'locality': "Chicago",
            #     'region': "IL",
            #     'postal_code': "60622"
            # }
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


# '''
# These are the (superset of) parameters that Braintree expects.
# '''
# expected_params  = {
#     'individual': {
#         'first_name': "Jane",
#         'last_name': "Doe",
#         'email': "jane@14ladders.com",
#         'phone': "5553334444",
#         'date_of_birth': "1981-11-19",
#         'ssn': "456-45-4567",
#         'address': {
#             'street_address': "111 Main St",
#             'locality': "Chicago",
#             'region': "IL",
#             'postal_code': "60622"
#         }
#     },
#     'business': {
#         'legal_name': "Jane's Ladders",
#         'dba_name': "Jane's Ladders",
#         'tax_id': "98-7654321",
#         'address': {
#             'street_address': "111 Main St",
#             'locality': "Chicago",
#             'region': "IL",
#             'postal_code': "60622"
#         }
#     },
#     'funding': {
#         'descriptor': "Blue Ladders",
#         'email': "funding@blueladders.com",
#         'mobile_phone': "5555555555",
#         'account_number': "1123581321",
#         'routing_number': "071101307",
#     },
#     "tos_accepted": True,
# }
