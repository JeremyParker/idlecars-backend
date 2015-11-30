# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase

from server.services import car_helpers
from server.services import car as car_service
from server import factories, models

def _get_listing_queryset():
    return car_service.filter_live(models.Car.objects.all())


class ListingTest(TestCase):
    def setUp(self):
        owner = factories.BankAccountOwner.create(state_code='NY')
        self.car = factories.BookableCar.create(
            owner=owner,
            status='available',
            next_available_date=timezone.now().date() + datetime.timedelta(days=1),
            min_lease='_03_two_weeks',
            hybrid=True,
        )

    def test_car_filtered_if_booking_in_progress(self):
        factories.ReservedBooking.create(car=self.car)
        self.assertEqual(len(_get_listing_queryset()), 0)

    def test_car_filtered_if_booking_booked(self):
        factories.BookedBooking.create(car=self.car)
        self.assertEqual(len(_get_listing_queryset()), 0)

    def test_car_shows_if_no_booking_in_progress(self):
        models.Booking.objects.all().delete()  # make sure there are no bookings on our car
        factories.Booking.create(car = self.car)            # PENDING
        factories.ReturnedBooking.create(car = self.car)    # RETURNED
        factories.RefundedBooking.create(car = self.car)    # REFUNDED
        factories.IncompleteBooking.create(car = self.car)  # INCOMPLETE
        self.assertEqual(len(_get_listing_queryset()), 1)

    def test_car_avialable_a_month_away(self):
        ''' car is not listed when it isn't available for another month '''
        self.car.next_available_date = timezone.now().date() + datetime.timedelta(days=31)
        self.car.status = 'busy'
        self.car.save()
        self.assertEqual(len(_get_listing_queryset()), 0)

    def test_car_unknown_availability_date(self):
        ''' car is not listed when busy and we don't know the available date '''
        self.car.next_available_date = None
        self.car.status = 'busy'
        self.car.save()
        self.assertEqual(len(_get_listing_queryset()), 0)

    def test_car_avialable_a_week_away(self):
        ''' car is listed if it's busy but will become available soon'''
        self.car.next_available_date = timezone.now().date() + datetime.timedelta(days=7)
        self.car.status = 'busy'
        self.car.save()
        self.assertEqual(len(_get_listing_queryset()), 1)

    def test_car_no_zipcode_no_show(self):
        self.car.owner.zipcode = ''
        self.car.owner.save()
        self.assertEqual(len(_get_listing_queryset()), 0)

    def test_car_with_zipcode_included(self):
        self.car.zipcode = '10022'
        self.car.save()
        self.assertEqual(len(_get_listing_queryset()), 1)

    def test_car_filtered_if_stale(self):
        ''' verify that a car is not listed when we haven't talked to the owner in a week'''
        self.car.last_status_update = timezone.now() - datetime.timedelta(days=7)
        self.car.save()
        self.assertEqual(len(_get_listing_queryset()), 0)

    def test_get_stale_soon_none(self):
        ''' verify that a car is not in the stale_soon results if it won't be stale soon. '''
        self.car.last_status_update = timezone.now()
        self.car.save()
        self.assertEqual(len(car_service.get_stale_within(120)), 0)

    def test_get_stale_soon_exists(self):
        ''' verify that stale_soon includes a car that is about to go stale. '''
        t = car_helpers.staleness_threshold + datetime.timedelta(minutes=5)
        self.car.last_status_update = t
        self.car.save()
        self.assertEqual(len(car_service.get_stale_within(120)), 1)

    def test_get_stale_soon_exluded_if_stale(self):
        ''' verify that stale_soon doesn't include stale cars. '''
        self.car.last_status_update = timezone.now() - datetime.timedelta(minutes=121)
        self.car.save()
        self.assertEqual(len(car_service.get_stale_within(120)), 0)

    def test_car_not_renewable_if_no_owner_bank_account(self):
        self.car.owner.merchant_account_state = models.Owner.BANK_ACCOUNT_DECLINED
        self.car.owner.save()
        self.assertEqual(len(car_service.get_stale_within(120)), 0)
