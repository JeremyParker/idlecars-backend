# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import os, sys
from random import randint

from django.core.management.base import BaseCommand
from django.conf import settings

from server.payment_gateways import test_braintree_params
from server import payment_gateways, factories, services, models


class Command(BaseCommand):
    help = '''
    This command tests the functionality of the braintree_payments library against the
    Braintree Sandbox environment. Where possible he data we send to Braintree here is
    the data the unit tests validate against.
    '''

    def _run_test(self, test_name, gateway):
        func = getattr(self, test_name)
        func(gateway)
        print '.'

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
            self._run_test('test_add_bank_account_business', g)
            self._run_test('test_add_payment_method', g)
            self._run_test('test_pre_authorize', g)
            self._run_test('test_void', g)
            self._run_test('test_settle', g)
            self._run_test('test_settle_fresh', g)
            self._run_test('test_escrow', g)
            self._run_test('test_escrow_fresh', g)

            self.owner.delete()
            self.driver.delete()

    def test_add_bank_account_failure(self, gateway):
        success, acct, error_fields, error_msgs = gateway.link_bank_account({'funding':{}})
        if not error_fields or not error_msgs:
            print 'test_add_bank_account_failure failed for gateway {}'.format(gateway)

    def test_add_bank_account_individual(self, gateway):
        params = test_braintree_params.individual_data['to_braintree']
        success, acct, error_fields, error_msgs = gateway.link_bank_account(params)
        if not success or not acct:
            print 'test_add_bank_account_individual failed for gateway {}'.format(gateway)
            print error_msgs
        self.owner.merchant_id = acct
        self.owner.save()

    def test_add_bank_account_business(self, gateway):
        params = test_braintree_params.business_data['to_braintree']
        success, acct, error_fields, error_msgs = gateway.link_bank_account(params)
        if not success or not acct:
            print 'test_add_bank_account_business failed for gateway {}'.format(gateway)
            print error_msgs
        self.owner.merchant_id = acct
        self.owner.save()

    def test_add_payment_method(self, gateway):
        success, card_info = gateway.add_payment_method(
            self.driver,
            test_braintree_params.VALID_VISA_NONCE,
        )
        if not success:
            print 'test_add_payment_method_and_pay failed to add payment_method for gateway {}'.format(gateway)
            return

        card_token, card_suffix, card_type, card_logo, exp, unique_number_identifier = card_info
        payment_method = models.PaymentMethod.objects.create(
            driver=self.driver,
            gateway_token=card_token,
            suffix=card_suffix,
            card_type=card_type,
            card_logo=card_logo,
            expiration_date=exp,
            unique_number_identifier=unique_number_identifier,
        )

    def _create_payment(self):
        '''
        This is a setUp method for a bunch of the tests below.
        '''
        car = factories.BookableCar.create(owner=self.owner)
        booking = factories.Booking.create(car=car, driver=self.driver)
        dollar_amount = '9.{}'.format(randint(1, 99)) # change so the gateway won't reject as dupe.
        return services.payment.create_payment(booking, dollar_amount)

    def test_pre_authorize(self, gateway):
        payment = self._create_payment()
        payment = gateway.pre_authorize(payment)
        if not payment.status == models.Payment.PRE_AUTHORIZED:
            print 'test_pre_authorize failed to authorize for {}'.format(gateway)
        if not payment.transaction_id:
            print 'test_pre_authorize failed to get a transaction id for {}'.format(gateway)

    def test_void(self, gateway):
        payment = self._create_payment()
        payment = gateway.pre_authorize(payment)
        payment = gateway.void(payment)
        if not payment.status == models.Payment.VOIDED:
            print 'test_void failed to void for {}'.format(gateway)

    def test_settle(self, gateway):
        payment = self._create_payment()
        payment = gateway.pre_authorize(payment)
        payment = gateway.settle(payment)
        if not payment.status == models.Payment.SETTLED:
            print 'test_settle failed to settle for {}'.format(gateway)

    def test_settle_fresh(self, gateway):
        ''' create a payment and go straight to SETTLED (as opposed to pre-authorizing first)'''
        payment = self._create_payment()
        payment = gateway.settle(payment)
        if not payment.status == models.Payment.SETTLED:
            print 'test_settle_fresh failed to settle for {}'.format(gateway)

    def test_escrow(self, gateway):
        payment = self._create_payment()
        payment = gateway.pre_authorize(payment)
        payment = gateway.escrow(payment)
        if not payment.status == models.Payment.HELD_IN_ESCROW:
            print 'test_escrow failed for {}'.format(gateway)

    def _create_escrow_payment(self, gateway):
        payment = self._create_payment()
        return gateway.escrow(payment)

    def test_escrow_fresh(self, gateway):
        payment = self._create_escrow_payment(gateway)
        if not payment.status == models.Payment.HELD_IN_ESCROW:
            print 'test_escrow_fresh failed for {}'.format(gateway)

    def test_refund(self, gateway):
        payment = self._create_escrow_payment(gateway)
        payment = gateway.refund(payment)
        if not payment.status == models.Payment.HELD_IN_ESCROW:
            print 'test_refund failed for {}'.format(gateway)
