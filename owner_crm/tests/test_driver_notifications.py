# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command

import server.factories

from owner_crm.tests import sample_merge_vars

from freezegun import freeze_time


''' Tests the cron job that sends delayed notifications to drivers '''
class TestDriverNotifications(TestCase):
    @freeze_time("2015-10-10 9:55:00")
    def _simulate_new_booking(self):
        driver = server.factories.Driver.create()
        return server.factories.Booking.create(driver=driver)

    def setUp(self):
        self.booking = self._simulate_new_booking()

    @freeze_time("2015-10-10 11:00:00")
    def test_docs_reminder(self):
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))
        self.assertEqual(
            outbox[0].subject,
            'Your {} is waiting on your driver documents'.format(self.booking.car.display_name())
        )

    @freeze_time("2015-10-10 11:00:00")
    def test_driver_no_booking(self):
        self.booking.delete()
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    @freeze_time("2015-10-10 11:00:00")
    def test_no_email_twice(self):
        call_command('driver_notifications')
        call_command('driver_notifications')
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    @freeze_time("2015-10-10 11:00:00")
    def test_only_new_driver_get_reminder(self):
        call_command('driver_notifications')
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        self._simulate_new_booking()
        call_command('driver_notifications')
        self.assertEqual(len(outbox), 2)

    ''' check that we don't send an email to a driver who already uploaded their docs '''
    @freeze_time("2015-10-10 11:00:00")
    def test_docs_reminder_driver_complete(self):
        self.booking.driver.delete()
        server.factories.CompletedDriver.create()
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_reminder_until_flake(self):
        #TODO: time should be from settings
        with freeze_time("2015-10-10 11:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')
        with freeze_time("2015-10-11 10:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')
        with freeze_time("2015-10-11 22:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')
        with freeze_time("2015-10-12 10:00:00"):
            call_command('driver_notifications')
            call_command('cron_job')

        from django.core.mail import outbox
        # We should have sent:
        # - 3 Timed driver reminders based on sign-up time
        # - 1 Driver notification when the driver's booking expired
        # - 1 notification to ops when the booking expired.
        self.assertEqual(len(outbox), 5)
