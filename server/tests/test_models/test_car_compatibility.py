# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server.factories import RideshareFlavorFactory, Car, MakeModel
from server.models import CarCompatibility

class TestCarCompatibility(TestCase):
    def setUp(self):
        self.non_compaitble = MakeModel.create(make='BMW', model='i3')
        self.delorean_2 = MakeModel.create(make='DMC', model='Delorean 2')

        self.uber_x = RideshareFlavorFactory.create(name='uberX', friendly_id='uber_x')
        self.uber_x.compatible_models.add(self.delorean_2)

    # PENDING: implementation of comaptibility logic

    # def test_new_car(self):
    #     car = Car.create(year=2021, make_model=self.delorean_2)
    #     self.assertTrue(CarCompatibility(car).uber_x())

    # def test_old_car(self):
    #     car = Car.create(year=1985, make_model=self.delorean_2)
    #     self.assertFalse(CarCompatibility(car).uber_x())

    # def test_non_compatible_model(self):
    #     car = Car.create(year=2021, make_model=self.non_compaitble)
    #     self.assertFalse(CarCompatibility(car).uber_x())
