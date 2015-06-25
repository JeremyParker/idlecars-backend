# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from collections import OrderedDict

from django.utils import timezone
from django.test import TestCase

from server.services import booking as booking_service
from server import factories, models


class BookingServiceTest(TestCase):
    def setUp(self):
        owner = factories.Owner.create(state_code='NY')
        make_model = factories.MakeModel.create()
        self.car = factories.Car.create(
            owner=owner,
            make_model=make_model,
            status='available',
            next_available_date=timezone.now().date() + datetime.timedelta(days=1),
            min_lease='_03_two_weeks',
            hybrid=True,
        )
        self.driver = factories.Driver.create()

    def test_create_booking_success(self):
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertIsNotNone(new_booking)
        self.assertEqual(new_booking.driver, self.driver)
        self.assertEqual(new_booking.car, self.car)

        # check the email that got sent
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'New Booking from {} {}'.format(self.driver.first_name(), self.driver.last_name())
        )
        self.assertEqual(
            outbox[0].merge_vars['support@idlecars.com']['CTA_URL'].split('/')[-2],
            unicode(new_booking.pk),
        )
