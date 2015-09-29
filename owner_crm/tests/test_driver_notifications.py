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
    def _simulate_new_driver(self):
        driver = server.factories.Driver.create()

        now = timezone.now()
        created_time = now - datetime.timedelta(hours=1, minutes=5)  # TODO(JP): get the time from config
        driver.auth_user.date_joined = created_time
        driver.auth_user.save()
        return driver

    def _simulate_new_booking(self):
        driver = self._simulate_new_driver()
        booking = server.factories.Booking.create(
            driver=driver,
            created_time=driver.auth_user.date_joined
        )
        return booking

    def setUp(self):
        self.booking = self._simulate_new_booking()

    def test_docs_reminder(self):
        call_command('driver_notifications')

        # TODO
        # from django.core.mail import outbox
        # self.assertEqual(len(outbox), 1)
        # self.assertTrue(sample_merge_vars.check_template_keys(outbox))

        # self.assertEqual(
        #     outbox[0].subject,
        #     'Your {} is waiting on your driving documents'.format(self.booking.car.display_name())
        # )

    def test_driver_no_booking(self):
        self.booking.delete()
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

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
        self.booking.driver.delete()
        server.factories.CompletedDriver.create()
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)
