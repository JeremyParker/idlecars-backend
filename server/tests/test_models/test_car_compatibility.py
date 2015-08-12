# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server.factories import RideshareFlavorFactory, Car, MakeModel
from server.models import CarCompatibility

class TestComaptibleMakeModel(TestCase):
    def setUp(self):
        self.non_compaitble = MakeModel.create(make='BMW', model='i3')
        self.delorean_2 = MakeModel.create(make='DMC', model='Delorean 2')

        self.uber_x = RideshareFlavorFactory.create(name='uberX', friendly_id='uber_x')
        self.uber_x.compatible_models.add(self.delorean_2)

    def test_compatible_model(self):
        car = Car.create(make_model=self.delorean_2)
        self.assertEqual(self.uber_x.name, CarCompatibility(car).uber_x())

    def test_non_compatible_model(self):
        car = Car.create(make_model=self.non_compaitble)
        self.assertFalse(CarCompatibility(car).uber_x())

# class TestLyft(TestCase):
#     def setUp(self):
#         self.lyft_standard = RideshareFlavorFactory.create(name='Lyft', friendly_id='lyft_standard')
#         self.lyft_plus = RideshareFlavorFactory.create(name='Lyft Plus', friendly_id='lyft_plus')

#     def test_compatible_model(self):
#         mm = MakeModel.create(passenger_count=42)
#         car = Car.create(make_model=mm)
#         self.assertEqual(self.lyft_standard.name, CarCompatibility(car).uber_x())

#     def test_non_compatible_model(self):
#         mm = MakeModel.create(passenger_count=42)
#         car = Car.create(make_model=mm)
#         self.assertEqual(self.lyft_plus.name, CarCompatibility(car).uber_x())
