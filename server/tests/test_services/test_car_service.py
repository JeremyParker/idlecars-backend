# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

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
