# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.utils import timezone

from server.factories import CompletedDriver, Booking
from server.services import payment as payment_service

class PaymentServiceTest(TestCase):
    def setUp(self):
        pass

    def test_create_payment_with_no_payment_method(self):
        driver = CompletedDriver.create()
        booking = Booking.create(driver=driver)
        payment = payment_service.create_payment(
            booking,
            amount = '66.66',
            service_fee = '0.00',
            invoice_start_time = timezone.now(),
            invoice_end_time = timezone.now(),
        )
        self.assertIsNotNone(payment.error_message)
