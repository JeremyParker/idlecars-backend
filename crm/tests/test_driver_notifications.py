# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command

import idlecars.client_side_routes
import server.models
import server.factories

from crm.tests import sample_merge_vars


class TestDriverNotifications(TestCase):
    ''' Tests the cron job that sends delayed notifications to drivers '''

    def test_docs_reminder(self):
        now = timezone.now()
        booking_time = now - datetime.timedelta(hours=24, minutes=1)  # TODO(JP): get the 24 from config

        driver = server.factories.Driver.create()
        car = server.factories.Car.create()
        booking = server.factories.Booking.create()
        booking.created_time = booking_time
        booking.save()

        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

        self.assertEqual(
            outbox[0].subject,
            'Your {} is waiting on your driving documents'.format(booking.car.__unicode__())
        )
