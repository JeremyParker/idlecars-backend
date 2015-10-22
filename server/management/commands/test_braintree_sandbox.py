# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import os, sys
from random import randint
from decimal import Decimal

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
            self._run_test('test_add_payment_method_error', g)
            self._run_test('test_pre_authorize_zero_dollars', g)
            self._run_test('test_void_zero_dollars', g)
            self._run_test('test_settle_zero_dollars', g)
            self._run_test('test_escrow_zero_dollars', g)
            self._run_test('test_pre_authorize_error', g)
            self._run_test('test_pre_authorize', g)
            self._run_test('test_void', g)
            self._run_test('test_settle', g)
            self._run_test('test_settle_fresh_error', g)
            self._run_test('test_settle_fresh', g)
            self._run_test('test_escrow', g)
            self._run_test('test_escrow_fresh', g)
            self._run_test('test_escrow_fresh_error', g)

            # This test is not working right now. Status has to be "Settled". We can't fake that.
            # self._run_test('test_refund', g)

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

    def test_add_payment_method_error(self, gateway):
        # we have to fake it for the fake gatway :(
        if gateway is payment_gateways.get_gateway('fake'):
            gateway.next_payment_method_response = (False, self.driver, 'Some fake error',)

        success, info = gateway.add_payment_method(
            self.driver,
            test_braintree_params.INVALID_PAYMENT_METHOD_NONCE,
        )
        if success:
            print 'test_add_payment_method_error failed to return False in {}'.format(gateway)
        if not isinstance(info, unicode):
            print 'test_add_payment_method_error failed to return an error string in {}'.format(gateway)

    def _create_payment(self):
        '''
        This is a setUp method for a bunch of the tests below.
        '''
        car = factories.BookableCar.create(owner=self.owner)
        booking = factories.Booking.create(car=car, driver=self.driver)
        dollar_amount = '9.{}'.format(randint(1, 99)) # change so the gateway won't reject as dupe.
        return services.payment.create_payment(booking, dollar_amount)

    def _create_zero_payment(self):
        payment = self._create_payment()
        payment.amount = Decimal('0.00')
        return payment

    def _create_error_payment(self, gateway):
        # we have to handle each gateway separately :(
        if gateway is payment_gateways.get_gateway('fake'):
            next_response = (models.Payment.DECLINED, 'This transaction was declined by the fake gateway.',)
            gateway.next_payment_response.append(next_response)

        car = factories.BookableCar.create(owner=self.owner)
        booking = factories.Booking.create(car=car, driver=self.driver, service_percentage='0.000')
        return services.payment.create_payment(booking, '2078.00')

    def test_pre_authorize_zero_dollars(self, gateway):
        payment = self._create_zero_payment()
        payment = gateway.pre_authorize(payment)
        if not payment.status == models.Payment.PRE_AUTHORIZED:
            print 'test_pre_authorize_zero_dollars failed to authorize for {}'.format(gateway)

    def test_void_zero_dollars(self, gateway):
        payment = self._create_zero_payment()
        payment = gateway.pre_authorize(payment)
        payment = gateway.void(payment)
        if not payment.status == models.Payment.VOIDED:
            print 'test_void_zero_dollars failed to void for {}'.format(gateway)

    def test_settle_zero_dollars(self, gateway):
        payment = self._create_zero_payment()
        payment = gateway.pre_authorize(payment)
        payment = gateway.settle(payment)
        if not payment.status == models.Payment.SETTLED:
            print 'test_settle_zero_dollars failed to void for {}'.format(gateway)

    def test_escrow_zero_dollars(self, gateway):
        payment = self._create_zero_payment()
        payment = gateway.pre_authorize(payment)
        payment = gateway.escrow(payment)
        if not payment.status == models.Payment.HELD_IN_ESCROW:
            print 'test_escrow_zero_dollars failed to void for {}'.format(gateway)

    def test_pre_authorize(self, gateway):
        payment = self._create_payment()
        payment = gateway.pre_authorize(payment)
        if not payment.status == models.Payment.PRE_AUTHORIZED:
            print 'test_pre_authorize failed to authorize for {}'.format(gateway)
        if not payment.transaction_id:
            print 'test_pre_authorize failed to get a transaction id for {}'.format(gateway)

    def test_pre_authorize_error(self, gateway):
        payment = self._create_error_payment(gateway)
        payment = gateway.pre_authorize(payment)
        if not payment.error_message:
            print '() test_pre_authorize_error: No error message!'.format(gateway)
        if payment.status != models.Payment.DECLINED:
            print '{} test_pre_authorize_error: Payment state != DECLINED'.format(gateway)

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

    def test_settle_fresh_error(self, gateway):
        payment = self._create_error_payment(gateway)
        payment = gateway.settle(payment)
        if not payment.error_message:
            print '{} test_settle_error: No error message!'.format(gateway)
        if payment.status != models.Payment.DECLINED:
            print '{} test_settle_error: Payment state != DECLINED'.format(gateway)

    def test_settle_fresh(self, gateway):
        ''' create a payment and go straight to SETTLED (as opposed to pre-authorizing first)'''
        payment = self._create_payment()
        payment = gateway.settle(payment)
        if not payment.status == models.Payment.SETTLED:
            print 'test_settle_fresh failed to settle for {}'.format(gateway)

    def test_escrow(self, gateway):
        payment = self._create_payment()
        payment = gateway.pre_authorize(payment)
        if payment.error_message:
            print 'test_escrow\'s pre_authorize call returned error{}'.format(payment.error_message)
        if payment.status != models.Payment.PRE_AUTHORIZED:
            print 'test_escrow\'s pre_authorize left status as {}'.format(payment.status)

        payment = gateway.escrow(payment)
        if payment.error_message:
            print 'test_escrow\'s escrow call returned error{}\n{}'.format(
                payment.error_message,
                payment.notes,
            )
        if not payment.status == models.Payment.HELD_IN_ESCROW:
            print 'test_escrow failed for {}'.format(gateway)

    def test_escrow_fresh_error(self, gateway):
        payment = self._create_error_payment(gateway)
        payment = gateway.escrow(payment)
        if not payment.error_message:
            print '{} test_escrow_fresh_error: No error message!'.format(gateway)
        if payment.status != models.Payment.DECLINED:
            print '{} test_escrow_fresh_error: Payment state != DECLINED'.format(gateway)

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
        if not payment.status == models.Payment.REFUNDED:
            print 'test_refund failed with {} for {}'.format(payment.error_message, gateway)
