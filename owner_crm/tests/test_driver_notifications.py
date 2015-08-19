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
    def setUp(self):
        now = timezone.now()
        booking_time = now - datetime.timedelta(hours=1, minutes=1)  # TODO(JP): get the time from config

        driver = server.factories.Driver.create()
        self.booking = server.factories.Booking.create(driver=driver)
        self.booking.created_time = booking_time
        self.booking.save()

    def test_docs_reminder(self):
        call_command('driver_notifications')

        # TODO
        # from django.core.mail import outbox
        # self.assertEqual(len(outbox), 1)
        # self.assertTrue(sample_merge_vars.check_template_keys(outbox))

        # self.assertEqual(
        #     outbox[0].subject,
        #     'Your {} is waiting on your driving documents'.format(self.booking.car.__unicode__())
        # )


    ''' check that we don't send an email to a driver who already uploaded their docs '''
    def test_docs_reminder_driver_complete(self):
        self.booking.driver = server.factories.CompletedDriver.create()
        self.booking.save()
        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)
