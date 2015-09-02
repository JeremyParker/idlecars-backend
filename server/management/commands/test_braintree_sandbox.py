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

    def _run_test(self, test_name, gateway):
        try:
            getattr(self, test_name)(gateway)
            print '.'
        except Exception as e:
            print "{} failed for {} with exception {}".format(test_name, gateway, e)

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
            self.owner = factories.Owner.create()
            self.driver = factories.Driver.create()

            self._run_test('test_add_bank_account_failure', g)
            self._run_test('test_add_bank_account_individual', g)
            self._run_test('test_add_payment_method', g)
            self._run_test('test_pay', g)

            self.owner.delete()
            self.driver.delete()

    def test_add_bank_account_failure(self, gateway):
        success, acct, error_fields, error_msgs = gateway.link_bank_account({'funding':{}})
        if not error_fields or not error_msgs:
            print 'test_add_bank_account_failure failed for gateway {}'.format(gateway)

    def test_add_bank_account_individual(self, gateway):
        success, acct, error_fields, error_msgs = gateway.link_bank_account(self.bank_account_params)
        if not success or not acct:
            print 'test_add_bank_account_individual failed for gateway {}'.format(gateway)
            print error_msgs
        self.owner.merchant_id = acct
        self.owner.save()

    def test_add_payment_method(self, gateway):
        success, card_info = gateway.add_payment_method(self.driver, VALID_VISA_NONCE)
        if not success:
            print 'test_add_payment_method_and_pay failed to add payment_method for gateway {}'.format(gateway)
            return

        card_token, card_suffix, card_type, card_logo, exp, unique_number_identifier = card_info

    def test_pay(self, gateway):
        if gateway == payment_gateways.get_gateway('fake'): # not integrated yet
            return

        # TODO - hook this up to the braintree_payemnts module
        # for now just manually make a payment just to proove that we've got all the bits in place
        request = {
            "merchant_account_id": self.owner.merchant_id,
            'amount': '10.50',
            "service_fee_amount": "1.00",
            'customer_id': self.driver.braintree_customer_id,
            'options': {
                'submit_for_settlement': True,
                # 'hold_in_escrow': escrow,
            },
        }

        import braintree
        response = braintree.Transaction.sale(request)
        success = getattr(response, 'is_success', False)
        if not success:
            print 'test_pay failed to pay for gateway {}'.format(gateway)
            return
