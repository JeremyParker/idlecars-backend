# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.test import TestCase
from django.utils import timezone

from server.factories import CompletedDriver, Booking
from server.services import payment as payment_service
from server.services import driver as driver_service
from server.services import payment_method as payment_method_service


class PaymentServiceTest(TestCase):
    def setUp(self):
        self.driver = CompletedDriver.create()
        self.booking = Booking.create(driver=self.driver)

    def test_create_payment_with_no_payment_method(self):
        payment = payment_service.create_payment(
            self.booking,
            amount = '66.66',
            service_fee = '0.00',
            invoice_start_time = timezone.now(),
            invoice_end_time = timezone.now(),
        )
        self.assertIsNotNone(payment.error_message)

    def test_create_payment_with_multiple_payment_method(self):
        # add a payment method
        payment_method_service.add_payment_method(self.driver, 'some_nonce')
        first_payment_method = driver_service.get_default_payment_method(self.driver)

        # add a second payment method
        payment_method_service.add_payment_method(self.driver, 'some_other_nonce')
        new_payment_method = driver_service.get_default_payment_method(self.driver)

        # the new_payment_method should not be the first payment method.
        self.assertNotEqual(first_payment_method, new_payment_method)

    def test_create_payment_with_app_credit(self):
        payment_method_service.add_payment_method(self.driver, 'some_nonce')
        self.driver.auth_user.customer.app_credit = decimal.Decimal('50.00')
        self.driver.auth_user.customer.save()
        payment = payment_service.create_payment(self.booking, amount = '56.66',)
        self.assertEqual(payment.credit_amount, decimal.Decimal('50.00'))
        self.assertEqual(payment.amount, decimal.Decimal('6.66'))
