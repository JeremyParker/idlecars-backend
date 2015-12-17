# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

import datetime
from freezegun import freeze_time

from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command

import credit.factories
import server.factories
from server.models import Booking
from owner_crm.tests import sample_merge_vars
from owner_crm.tests.test_services import test_message


''' Tests the cron job that sends delayed notifications to drivers '''
class TestDriverDocsNotifications(TestCase):
    @freeze_time("2014-10-10 9:55:00")
    def _simulate_new_booking(self):
        driver = server.factories.Driver.create()
        return server.factories.Booking.create(driver=driver)

    def setUp(self):
        self.booking = self._simulate_new_booking()

    @freeze_time("2014-10-10 11:00:00")
    def test_docs_reminder(self):
        call_command('driver_notifications')

        test_message.verify_throttled_on_driver(
            self.booking.driver,
            'first_documents_reminder'
        )

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))
        self.assertEqual(
            outbox[0].subject,
            'Your {} is waiting on your driver documents'.format(self.booking.car.display_name())
        )

    @freeze_time("2014-10-10 11:00:00")
    def test_driver_no_booking(self):
        driver = self.booking.driver
        self.booking.delete()
        call_command('driver_notifications')
        test_message.verify_throttled_on_driver(
            driver,
            'first_documents_reminder',
        )

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    @freeze_time("2014-10-10 11:00:00")
    def test_no_email_twice(self):
        call_command('driver_notifications')
        test_message.verify_throttled_on_driver(
            self.booking.driver,
            'first_documents_reminder'
        )

        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    @freeze_time("2014-10-10 11:00:00")
    def test_only_new_driver_get_reminder(self):
        call_command('driver_notifications')
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        self._simulate_new_booking()
        call_command('driver_notifications')
        self.assertEqual(len(outbox), 2)

    ''' check that we don't send an email to a driver who already uploaded their docs '''
    @freeze_time("2014-10-10 11:00:00")
    def test_docs_reminder_driver_complete(self):
        self.booking.driver.delete()
        server.factories.CompletedDriver.create()
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_reminder_until_flake(self):
        with freeze_time("2014-10-10 9:55:00"):
            other_driver = server.factories.CompletedDriver.create()
            other_booking = server.factories.Booking.create(driver=other_driver)

        #TODO: time should be from settings
        with freeze_time("2014-10-10 11:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')
        test_message.verify_throttled_on_driver(
            self.booking.driver,
            'first_documents_reminder'
        )
        with freeze_time("2014-10-11 10:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')
        test_message.verify_throttled_on_driver(
            self.booking.driver,
            'second_documents_reminder'
        )
        with freeze_time("2014-10-11 22:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')
        with freeze_time("2014-10-12 10:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')
        test_message.verify_throttled_on_driver(
            self.booking.driver,
            'third_documents_reminder'
        )
        with freeze_time("2014-10-13 10:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')

        from django.core.mail import outbox
        '''
        We should have sent:
        - 3 Timed document reminders based on sign-up time for driver without docs
        - 2 Driver notification when the drivers' bookings expired
        '''
        self.assertEqual(len(outbox), 5)

        self.assertEqual(
            outbox[3].subject,
            'Your rental has been cancelled because we don\'t have your driver documents.'
        )
        self.assertEqual(
            outbox[4].subject,
            'Your {} rental has been cancelled because you never checked out.'.format(
                other_booking.car.display_name()
            )
        )

        # each booking should have been set to the correct INCOMPLETE reason
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.get_state(), Booking.INCOMPLETE)
        self.assertEqual(self.booking.incomplete_reason, Booking.REASON_DRIVER_TOO_SLOW_DOCS)

        other_booking.refresh_from_db()
        self.assertEqual(other_booking.get_state(), Booking.INCOMPLETE)
        self.assertEqual(other_booking.incomplete_reason, Booking.REASON_DRIVER_TOO_SLOW_CC)


class TestDriverCreditNotifications(TestCase):
    @freeze_time("2014-10-10 9:55:00")
    def setUp(self):
        self.poor_driver = server.factories.ApprovedDriver.create()

        # rich driver signed up with a credit code, but hasn't spend the credit yet.
        self.rich_driver = server.factories.ApprovedDriver.create()
        self.rich_driver.auth_user.customer.invitor_code = credit.factories.CreditCode.create()
        self.rich_driver.auth_user.customer.invitor_credited = False
        self.rich_driver.auth_user.customer.app_credit = Decimal('50.00')
        self.rich_driver.auth_user.customer.save()

    def test_poor_driver_no_credit_reminder(self):
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 3)
        self.assertEqual(
            outbox[0].subject,
            'You have ${} to use towards your next rental'.format(self.rich_driver.app_credit())
        )
        self.assertEqual(
            outbox[1].subject,
            'Let us give you cash towards your rental',
        )
        self.assertEqual(
            outbox[2].subject,
            'Let us give you cash towards your rental',
        )

    @freeze_time("2014-10-23 8:55:00")
    def test_reminder_delay(self):
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_no_email_twice(self):
        call_command('driver_notifications')
        call_command('driver_notifications')
        call_command('driver_notifications')

        from django.core.mail import outbox
        '''
        1. app credit reminder to rich_driver
        2. coupon reminder to poor driver
        3. coupon reminder to rich driver
        '''
        self.assertEqual(len(outbox), 3)

    def test_no_credit_email_with_active_booking(self):
        server.factories.BookedBooking.create(driver=self.rich_driver)
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_no_credit_email_with_accepted_booking(self):
        server.factories.AcceptedBooking.create(driver=self.rich_driver)
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_no_credit_email_with_requested_booking(self):
        server.factories.RequestedBooking.create(driver=self.rich_driver)
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_no_credit_email_with_reserved_booking(self):
        server.factories.ReservedBooking.create(driver=self.rich_driver)
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
