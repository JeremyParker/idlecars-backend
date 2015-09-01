# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from braintree.test.nonces import Nonces

from django.core.management.base import BaseCommand
from django.conf import settings

from server import payment_gateways, factories

VALID_ROUTING_NUMBER = '071101307'
VALID_VISA_NONCE = Nonces.TransactableVisa


class Command(BaseCommand):
    help = '''
    This command will test the functionality of the braintree_payments library against the
    Braintree Sandbox environment. Also, we'll confirm that the fake_payments gateway acts
    the same.
    '''

    bank_account_params =  {
        'individual': {
            'first_name': "Jane",
            'last_name': "Doe",
            'email': "jane@14ladders.com",
            'phone': "5553334444",
            'date_of_birth': "1981-11-19",
            'ssn': "456-45-4567",
            'address': {
                'street_address': "111 Main St",
                'locality': "Chicago",
                'region': "IL",
                'postal_code': "60622"
            }
        },
        'business': {
            'legal_name': "Jane's Ladders",
            'dba_name': "Jane's Ladders",
            'tax_id': "98-7654321",
            'address': {
                'street_address': "111 Main St",
                'locality': "Chicago",
                'region': "IL",
                'postal_code': "60622"
            }
        },
        'funding': {
            'descriptor': "Blue Ladders",
            'email': "funding@blueladders.com",
            'mobile_phone': "5555555555",
            'account_number': "1123581321",
            'routing_number': VALID_ROUTING_NUMBER,
        },
        "tos_accepted": True,
    }

    def handle(self, *args, **options):
        # make sure braintree is set to use the sandbox!
        config = settings.BRAINTREE
        if config['environment'] != 'Sandbox':
            raise Exception('Woah! We shouldn\'t be running this on anything but Sandbox')

        gateways = [
            payment_gateways.get_gateway('braintree'),
            payment_gateways.get_gateway('fake')
        ]
        for g in gateways:
            self.test_add_bank_account_individual(g)
            self.test_add_bank_account_failure(g)
            self.test_add_payment_method_and_pay(g)

    def test_add_bank_account_individual(self, gateway):
        success, acct, error_fields, error_msgs = gateway.link_bank_account(self.bank_account_params)
        if not success or not acct:
            print 'test_add_bank_account_individual failed for gateway {}'.format(gateway)
            print error_msgs

    def test_add_bank_account_failure(self, gateway):
        success, acct, error_fields, error_msgs = gateway.link_bank_account({'funding':{}})
        if not error_fields or not error_msgs:
            print 'test_add_bank_account_failure failed for gateway {}'.format(gateway)

    # def test_add_payment_method_and_pay(self, gateway):
    #     import pdb; pdb.set_trace()
    #     driver = factories.Driver.create()
    #     success, card_info = gateway.add_payment_method(driver, VALID_VISA_NONCE)
    #     if success:
    #         card_token, card_suffix, card_type, card_logo, exp, unique_number_identifier = card_info
    #     else:
    #         print 'test_add_payment_method_and_pay failed for gateway {}'.format(gateway)

