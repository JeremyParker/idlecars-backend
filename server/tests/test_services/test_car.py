# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from server import factories, models, services


class CarTest(TestCase):
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

    def test_car_filtered_if_booking_in_progress(self):
        ''' verify that a car is not listed when it has a booking in progress '''
        booking = factories.Booking.create(car=self.car)
        for state in [
            models.Booking.COMPLETE,
            models.Booking.REQUESTED,
            models.Booking.ACCEPTED,
        ]:
            booking.state = state
            booking.save()
            self.assertEqual(len(services.car.listing_queryset.all()), 0)

    def test_car_shows_if_no_booking_in_progress(self):
        ''' verify that a car is listed when it has no booking in progress '''
        models.Booking.objects.all().delete()  # make sure there are no bookings on our car
        for state in [
            models.Booking.PENDING,
            models.Booking.BOOKED,
            models.Booking.FLAKE,
            models.Booking.TOO_SLOW,
            models.Booking.OWNER_REJECTED,
            models.Booking.DRIVER_REJECTED,
            models.Booking.MISSED,
        ]:
            factories.Booking.create(
                car = self.car,
                state = state,
            )
            self.assertEqual(len(services.car.listing_queryset.all()), 1)

    def test_car_avialable_a_month_away(self):
        ''' car is not listed when it isn't available for another month '''
        self.car.next_available_date = datetime.date.today() + datetime.timedelta(days=31)
        self.car.status = 'busy'
        self.car.save()
        self.assertEqual(len(services.car.listing_queryset.all()), 0)

    def test_car_unknown_availability_date(self):
        ''' car is not listed when we don't know the available date '''
        self.car.next_available_date = None
        self.car.status = 'busy'
        self.car.save()
        self.assertEqual(len(services.car.listing_queryset.all()), 0)

    def test_car_avialable_a_week_away(self):
        ''' car is listed if it's busy but will become available soon'''
        self.car.next_available_date = datetime.date.today() + datetime.timedelta(days=7)
        self.car.status = 'busy'
        self.car.save()
        self.assertEqual(len(services.car.listing_queryset.all()), 1)

    def test_car_no_zipcode_no_show(self):
        self.car.owner.zipcode = ''
        self.car.owner.save()
        self.assertEqual(len(services.car.listing_queryset.all()), 0)

    def test_car_with_zipcode_included(self):
        self.car.zipcode = '10022'
        self.car.save()
        self.assertEqual(len(services.car.listing_queryset.all()), 1)

    def test_car_filtered_if_stale(self):
        ''' verify that a car is not listed when we haven't talked to the owner in a week'''
        self.car.owner.last_engagement = datetime.date.today() - datetime.timedelta(days=7)
        self.car.owner.save()
        self.assertEqual(len(services.car.listing_queryset.all()), 0)
