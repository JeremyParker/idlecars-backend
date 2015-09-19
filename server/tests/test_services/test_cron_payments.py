# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command

from owner_crm.tests import sample_merge_vars

from server import factories, payment_gateways
from server.models import Payment
from server.services import booking as booking_service


''' Tests the cron job that creates recurring payments '''
class TestCronPayments(TestCase):
    def setUp(self):
        self.driver = factories.PaymentMethodDriver.create(documentation_approved=True)
        self.owner = factories.BankAccountOwner.create()
        self.car = factories.BookableCar.create(owner=self.owner)

        self.booking = factories.AcceptedBooking.create(
            car=self.car,
            driver=self.driver,
        )

        # simulate pickup that happened a week ago
        deposit = self.booking.payment_set.last()
        deposit.status = Payment.HELD_IN_ESCROW
        deposit.save()
        self.assertEqual(self.booking.payment_set.filter(status=Payment.HELD_IN_ESCROW).count(), 1)

        self.now = timezone.now().replace(microsecond=0)
        self.pickup_time = self.now - datetime.timedelta(days=7)
        self.first_rent_payment = factories.Payment.create(
            booking=self.booking,
            amount=self.booking.car.solo_cost,
            service_fee='50.00',
            invoice_start_time=self.pickup_time,
            invoice_end_time=self.now - datetime.timedelta(seconds=1),
            status=Payment.SETTLED,
        )
        self.booking.pickup_time = self.pickup_time
        self.booking.save()

        # there should be the deposit and the first week's rent paid.
        self.assertEqual(self.booking.payment_set.count(), 2)

    def test_make_payment_when_due(self):
        call_command('cron_payments')
        self.assertEqual(self.booking.payment_set.count(), 3)
        self.assertEqual(self.booking.payment_set.filter(status=Payment.HELD_IN_ESCROW).count(), 1)
        self.assertEqual(self.booking.payment_set.filter(status=Payment.SETTLED).count(), 2)

        # make sure we don't add any payments the next time we call cron_payments
        call_command('cron_payments')
        self.assertEqual(self.booking.payment_set.count(), 3)
        self.assertEqual(self.booking.payment_set.filter(status=Payment.HELD_IN_ESCROW).count(), 1)
        self.assertEqual(self.booking.payment_set.filter(status=Payment.SETTLED).count(), 2)

    def test_correct_time_range_with_many_past_payments(self):
        # make another payment from the previous week
        previous_rent_payment = factories.Payment.create(
            booking=self.booking,
            amount=self.booking.car.solo_cost,
            service_fee='50.00',
            invoice_start_time=self.pickup_time - datetime.timedelta(days=7),
            invoice_end_time=self.now - datetime.timedelta(days=7, seconds=1),
        )
        call_command('cron_payments')
        self.assertEqual(self.booking.payment_set.count(), 4)

        new_payment = self.booking.payment_set.filter(
            status=Payment.SETTLED,
        ).order_by('invoice_end_time').last()

        self.assertEqual(
            self.first_rent_payment.invoice_end_time + datetime.timedelta(seconds=1),
            new_payment.invoice_start_time,
        )
        self.assertEqual(
            self.first_rent_payment.invoice_end_time + datetime.timedelta(days=7),
            new_payment.invoice_end_time,
        )

    def test_non_settled_payment_sends_email(self):
        gateway = payment_gateways.get_gateway('fake')
        gateway.push_next_payment_response((Payment.DECLINED, 'Sorry, your card failed',))
        call_command('cron_payments')
        self.assertEqual(self.booking.payment_set.count(), 3)
        self.assertEqual(self.booking.payment_set.filter(status=Payment.DECLINED).count(), 1)

        # check what emails got sent
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_exception_doesnt_kill_job(self):
        gateway = payment_gateways.get_gateway('fake')
        gateway.push_next_payment_response('exception') # <-- This will make it throw an exception
        call_command('cron_payments')

        # check what emails got sent
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_no_payment_for_ended_booking(self):
        # the booking ended at the end of the last invoice payment period
        self.booking.end_time = self.first_rent_payment.invoice_end_time
        self.booking.save()

        call_command('cron_payments')
        self.assertEqual(self.booking.payment_set.count(), 2)  # no new payments

    def test_final_payment_is_partial_week(self):
        # TODO
        pass
