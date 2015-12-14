# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from server.factories import CompletedDriver, Booking
from server.services import invoice_service
from server.services import payment_method as payment_method_service


class InvoiceServiceTest(TestCase):
    def setUp(self):
        self.driver = CompletedDriver.create()
        payment_method_service.add_payment_method(self.driver, 'some_nonce')
        self.booking = Booking.create(
            driver=self.driver,
            weekly_rent=decimal.Decimal('100.00'),
            service_percentage=decimal.Decimal('0.10'),
            pickup_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=14),
        )

    def _give_driver_credit(self, credit):
        self.driver.auth_user.customer.app_credit = credit
        self.driver.auth_user.customer.save()

    def _sanity_check(self, booking, payment):
        # amount the driver paid should equal the car's weekly rent
        self.assertEqual(booking.weekly_rent, payment.amount + payment.credit_amount)
        # amount that got paid out should equal rent - service_fee
        owner_due = booking.weekly_rent - (booking.weekly_rent * booking.service_percentage)
        self.assertEqual(owner_due, (payment.amount - payment.service_fee) + payment.idlecars_supplement)

    def test_create_payment_with_all_app_credit(self):
        self._give_driver_credit(decimal.Decimal('500.00'))
        payment = invoice_service.create_next_rent_payment(self.booking)

        self.assertEqual(payment.amount, decimal.Decimal('0.00'))
        self.assertEqual(payment.credit_amount, decimal.Decimal('100.00'))
        self.assertEqual(payment.service_fee, decimal.Decimal('0.00'))
        self.assertEqual(payment.idlecars_supplement, decimal.Decimal('90.00'))
        self._sanity_check(self.booking, payment)

    def test_create_payment_with_some_app_credit(self):
        self._give_driver_credit(decimal.Decimal('5.00'))
        payment = invoice_service.create_next_rent_payment(self.booking)

        self.assertEqual(payment.amount, decimal.Decimal('95.00'))
        self.assertEqual(payment.credit_amount, decimal.Decimal('5.00'))
        self.assertEqual(payment.service_fee, decimal.Decimal('5.00'))
        self.assertEqual(payment.idlecars_supplement, decimal.Decimal('0.00'))
        self._sanity_check(self.booking, payment)

    def test_credit_no_service_fee(self):
        self._give_driver_credit(decimal.Decimal('5.00'))
        self.booking.service_percentage = decimal.Decimal('0.00')
        self.booking.save()
        payment = invoice_service.create_next_rent_payment(self.booking)

        self.assertEqual(payment.amount, decimal.Decimal('95.00'))
        self.assertEqual(payment.credit_amount, decimal.Decimal('5.00'))
        self.assertEqual(payment.service_fee, decimal.Decimal('0.00'))
        self.assertEqual(payment.idlecars_supplement, decimal.Decimal('5.00'))
        self._sanity_check(self.booking, payment)

    def test_credit_equal_to_service_fee(self):
        self._give_driver_credit(decimal.Decimal('10.00'))
        payment = invoice_service.create_next_rent_payment(self.booking)

        self.assertEqual(payment.amount, decimal.Decimal('90.00'))
        self.assertEqual(payment.credit_amount, decimal.Decimal('10.00'))
        self.assertEqual(payment.service_fee, decimal.Decimal('0.00'))
        self.assertEqual(payment.idlecars_supplement, decimal.Decimal('0.00'))
        self._sanity_check(self.booking, payment)

    def test_credit_greater_than_service_fee(self):
        self._give_driver_credit(decimal.Decimal('20.00'))
        payment = invoice_service.create_next_rent_payment(self.booking)

        self.assertEqual(payment.amount, decimal.Decimal('80.00'))
        self.assertEqual(payment.credit_amount, decimal.Decimal('20.00'))
        self.assertEqual(payment.service_fee, decimal.Decimal('0.00'))
        self.assertEqual(payment.idlecars_supplement, decimal.Decimal('10.00'))
        self._sanity_check(self.booking, payment)
