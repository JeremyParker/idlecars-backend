# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from freezegun import freeze_time

from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command

import server.factories
from server.models import Booking
from owner_crm.tests import sample_merge_vars



''' Tests the cron job that sends delayed notifications to drivers '''
class TestDriverNotifications(TestCase):
    @freeze_time("2014-10-10 9:55:00")
    def _simulate_new_booking(self):
        driver = server.factories.Driver.create()
        return server.factories.Booking.create(driver=driver)

    def setUp(self):
        self.booking = self._simulate_new_booking()

    @freeze_time("2014-10-10 11:00:00")
    def test_docs_reminder(self):
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))
        self.assertEqual(
            outbox[0].subject,
            'Your {} is waiting on your driver documents'.format(self.booking.car.display_name())
        )

    @freeze_time("2014-10-10 11:00:00")
    def test_driver_no_booking(self):
        self.booking.delete()
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    @freeze_time("2014-10-10 11:00:00")
    def test_no_email_twice(self):
        call_command('driver_notifications')
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
        with freeze_time("2014-10-11 10:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')
        with freeze_time("2014-10-11 22:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')
        with freeze_time("2014-10-12 10:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')
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
            'Your booking has been cancelled because we don\'t have your driver documents.'
        )
        self.assertEqual(
            outbox[4].subject,
            'Your {} booking has been cancelled because you never checked out.'.format(
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
