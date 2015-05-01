# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from collections import OrderedDict

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
            next_available_date=datetime.date.today() + datetime.timedelta(days=1),
            min_lease='_03_two_weeks',
            hybrid=True,
        )
        self.user_data = OrderedDict([
            ('email', 'joe@tester.org'),
            ('first_name', 'Joe'),
            ('last_name', 'Tested'),
            ('phone_number', '212 123 4567')
        ])

    def test_booking_from_new_driver(self):
        ''' verify that a new driver user can create a booking on a valid car '''
        with self.assertRaises(models.UserAccount.DoesNotExist):
            # make sure the user doesn't already exist
            models.UserAccount.objects.get(email=self.user_data['email'])

        new_booking = booking_service.create_booking(self.user_data, self.car)
        self.assertIsNotNone(new_booking)
        self.assertEqual(new_booking.user_account.email, self.user_data['email'])
        self.assertEqual(new_booking.car, self.car)

    def test_booking_from_existing_driver(self):
        ''' verify that an existing driver user can create a booking on a valid car '''
        first_booking = booking_service.create_booking(self.user_data, self.car)
        second_booking = booking_service.create_booking(self.user_data, self.car)

        # they should both be the same user
        self.assertEqual(first_booking.user_account.pk, second_booking.user_account.pk)
