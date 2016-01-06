# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.test import TestCase

from server.services import car as car_service
from server import factories, models


class CarCreateTest(TestCase):
    def setUp(self):
        self.owner = factories.BankAccountOwner.create(state_code='NY')
        self.plate = 'A REAL PLATE'

        # note: this MakeModel depends on the fake data we got from tlc lookup
        self.make_model = factories.MakeModel.create(make='Chevrolet', model="Camaro")

    def test_create_success(self):
        new_car = car_service.create_car(self.owner, self.plate)
        self.assertIsNotNone(new_car)
        self.assertEqual(new_car.plate, self.plate)
        self.assertEqual(new_car.owner, self.owner)

        # check the stuff we looked up in the TLC db:
        self.assertIsNotNone(new_car.base)
        self.assertIsNotNone(new_car.year)

        # check the info we got from the VIN
        self.assertEqual(new_car.make_model, self.make_model)

    def test_create_existing_with_no_owner(self):
        car = factories.Car.create(plate=self.plate)
        new_car = car_service.create_car(self.owner, self.plate)
        self.assertIsNotNone(new_car)
        self.assertEqual(new_car.plate, self.plate)
        self.assertEqual(new_car.owner, self.owner)

    def test_create_existing_with_other_owner(self):
        car = factories.ClaimedCar.create(plate=self.plate)
        with self.assertRaises(car_service.CarDuplicateException):
            new_car = car_service.create_car(self.owner, self.plate)

    def test_create_existing_my_car(self):
        car = factories.ClaimedCar.create(plate=self.plate, owner=self.owner)
        with self.assertRaises(car_service.CarDuplicateException):
            new_car = car_service.create_car(self.owner, self.plate)

    def test_create_not_in_tlc_db(self):
        with self.assertRaises(car_service.CarTLCException):
            new_car = car_service.create_car(self.owner, 'ERROR NOT FOUND')


class CarRecommendedRentTest(TestCase):
    def setUp(self):
        self.owner = factories.BankAccountOwner.create(state_code='NY')
        self.plate = 'A REAL PLATE'
        self.make_model = factories.MakeModel.create(make='Chevrolet', model="Camaro")

        self.car = car_service.create_car(self.owner, self.plate)

    def _create_car(self, rent):
        return factories.BookableCar.create(
            make_model=self.make_model,
            year=self.car.year,
            weekly_rent=Decimal(rent),
        )

    def _create_booking(self, booking_type, rent):
        return getattr(factories, booking_type).create(car=self._create_car(rent))

    def test_convicted_price_cars(self):
        booking_1 = self._create_booking('ReservedBooking', 500)
        booking_2 = self._create_booking('RequestedBooking', 600)
        booking_3 = self._create_booking('AcceptedBooking', 700)
        booking_4 = self._create_booking('BookedBooking', 900)
        booking_5 = self._create_booking('ReturnedBooking', 300)
        booking_6 = self._create_booking('RefundedBooking', 400)

        self.assertEqual(self.car.shift, models.Car.SHIFT_UNKNOWN)
        self.assertEqual(self.car.weekly_rent, None)
        self.car.shift = models.Car.SHIFT_FULL_TIME
        self.car.save()
        self.assertEqual(self.car.weekly_rent, Decimal(400))

    def test_attractive_price_cars(self):
        booking_1 = self._create_booking('Booking', 450)
        booking_2 = self._create_booking('Booking', 550)

        self.car.shift = models.Car.SHIFT_FULL_TIME
        self.car.save()
        self.assertEqual(self.car.weekly_rent, Decimal(450))

    def test_listable_price_cars(self):
        car_1 = self._create_car(500)
        car_2 = self._create_car(600)

        self.car.shift = models.Car.SHIFT_FULL_TIME
        self.car.save()
        self.assertEqual(self.car.weekly_rent, Decimal(450))

    def test_no_similar_cars(self):
        self.car.shift = models.Car.SHIFT_FULL_TIME
        self.car.save()
        self.assertEqual(self.car.weekly_rent, None)
