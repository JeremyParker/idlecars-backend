# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command

import server.factories

from owner_crm.tests import sample_merge_vars


''' Tests the cron job that sends delayed notifications to drivers '''
class TestDriverNotifications(TestCase):
    def _simulate_new_booking(self):
        driver = server.factories.Driver.create()
        booking = server.factories.Booking.create(driver=driver)

        now = timezone.now()
        booking_time = now - datetime.timedelta(hours=1, minutes=5)  # TODO(JP): get the time from config
        booking.created_time = booking_time
        booking.save()
        return booking

    def setUp(self):
        driver = server.factories.Driver.create()
        self.booking = self._simulate_new_booking()

    def test_docs_reminder(self):
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

        self.assertEqual(
            outbox[0].subject,
            'Your {} is waiting on your driving documents'.format(self.booking.car.display_name())
        )

    def test_no_email_twice(self):
        call_command('driver_notifications')
        call_command('driver_notifications')
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_only_new_driver_get_reminder(self):
        call_command('driver_notifications')
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        self._simulate_new_booking()
        call_command('driver_notifications')
        self.assertEqual(len(outbox), 2)

    ''' check that we don't send an email to a driver who already uploaded their docs '''
    def test_docs_reminder_driver_complete(self):
        self.booking.driver = server.factories.CompletedDriver.create()
        self.booking.save()
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)
