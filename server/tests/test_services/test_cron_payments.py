# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal, ROUND_UP

from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command

from owner_crm.tests import sample_merge_vars

from server import factories, payment_gateways
from server.models import Payment
from server.services import booking as booking_service

from freezegun import freeze_time


''' Tests the cron job that creates recurring payments '''
class TestCronPayments(TestCase):
    @freeze_time("2014-10-10 9:55:00")
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
            amount=self.booking.weekly_rent,
            service_fee='50.00',
            invoice_start_time=self.pickup_time,
            invoice_end_time=self.now,
            status=Payment.SETTLED,
        )
        self.booking.pickup_time = self.pickup_time
        self.booking.save()

        # there should be the deposit and the first week's rent paid.
        self.assertEqual(self.booking.payment_set.count(), 2)

    def test_make_payment_when_due(self):
        with freeze_time("2014-10-10 9:55:00"):
            call_command('cron_job')
            self.assertEqual(self.booking.payment_set.count(), 3)
            self.assertEqual(self.booking.payment_set.filter(status=Payment.HELD_IN_ESCROW).count(), 1)
            self.assertEqual(self.booking.payment_set.filter(status=Payment.SETTLED).count(), 2)

            # make sure we don't add any payments the next time we call cron_job
            call_command('cron_job')
            self.assertEqual(self.booking.payment_set.count(), 3)
            self.assertEqual(self.booking.payment_set.filter(status=Payment.HELD_IN_ESCROW).count(), 1)
            self.assertEqual(self.booking.payment_set.filter(status=Payment.SETTLED).count(), 2)

    def test_correct_time_range_with_many_past_payments(self):
        # make another payment from the previous week
        previous_rent_payment = factories.Payment.create(
            booking=self.booking,
            amount=self.booking.weekly_rent,
            service_fee='50.00',
            invoice_start_time=self.pickup_time - datetime.timedelta(days=7),
            invoice_end_time=self.now - datetime.timedelta(days=7),
        )
        call_command('cron_job')
        self.assertEqual(self.booking.payment_set.count(), 4)

        most_recent_payment = self.booking.payment_set.filter(
            status=Payment.SETTLED,
        ).order_by('invoice_end_time').last()

        self.assertEqual(
            self.first_rent_payment.invoice_end_time,
            most_recent_payment.invoice_start_time,
        )
        self.assertEqual(
            self.first_rent_payment.invoice_end_time + datetime.timedelta(days=7),
            most_recent_payment.invoice_end_time,
        )

    def test_non_settled_payment_sends_email(self):
        gateway = payment_gateways.get_gateway('fake')
        gateway.push_next_payment_response((Payment.DECLINED, 'Sorry, your card failed',))
        call_command('cron_job')
        self.assertEqual(self.booking.payment_set.count(), 3)
        self.assertEqual(self.booking.payment_set.filter(status=Payment.DECLINED).count(), 1)

        # check what emails got sent
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_exception_doesnt_kill_job(self):
        gateway = payment_gateways.get_gateway('fake')
        gateway.push_next_payment_response('ignore this output') # <-- This will make it throw an exception
        call_command('cron_job')

        # check what emails got sent
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_no_payment_for_ended_booking(self):
        # the booking ended at the end of the last invoice payment period
        self.booking.end_time = self.first_rent_payment.invoice_end_time
        self.booking.save()

        call_command('cron_job')
        self.assertEqual(self.booking.payment_set.count(), 2)  # no new payments

    def test_final_payment_is_partial_week(self):
        self.booking.end_time = self.first_rent_payment.invoice_end_time + datetime.timedelta(days=2)
        self.booking.save()
        call_command('cron_job')

        self.assertEqual(self.booking.payment_set.count(), 3)

        most_recent_payment = self.booking.payment_set.filter(
            status=Payment.SETTLED
        ).order_by(
            'invoice_end_time'
        ).last()
        daily_rent = self.booking.weekly_rent / Decimal('7.00')
        expected_amount = (daily_rent * Decimal('2.00')).quantize(Decimal('.01'), rounding=ROUND_UP)
        self.assertEqual(most_recent_payment.amount, expected_amount)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)
        self.assertEqual(
            outbox[0].subject,
            'Payment Received: {} Booking'.format(self.booking.car.display_name())
        )
        self.assertTrue('This is your last payment' in outbox[0].merge_vars[self.booking.driver.email()]['TEXT'])
        owner_email = self.booking.car.owner.auth_users.first().email
        self.assertTrue('This is the last payment' in outbox[1].merge_vars[owner_email]['TEXT'])

    def test_multiple_cron_payment_email(self):
        with freeze_time("2014-10-20 9:55:00"):
            self.booking.end_time = timezone.now()
            self.booking.save()

        with freeze_time("2014-10-10 9:55:00"):
            call_command('cron_job')
        with freeze_time("2014-10-17 9:55:00"):
            call_command('cron_job')

        from django.core.mail import outbox
        driver_email = self.booking.driver.email()
        owner_email = self.booking.car.owner.auth_users.first().email
        # we should have sent two receipts to the driver and two notifications to the owner.
        self.assertEqual(len(outbox), 4)
        self.assertTrue('Your next payment of' in outbox[0].merge_vars[driver_email]['TEXT'])
        self.assertTrue('The next payment of' in outbox[1].merge_vars[owner_email]['TEXT'])
        self.assertTrue('This is your last payment' in outbox[2].merge_vars[driver_email]['TEXT'])
        self.assertTrue('This is the last payment' in outbox[3].merge_vars[owner_email]['TEXT'])
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))
