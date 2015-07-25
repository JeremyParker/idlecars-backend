# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server.factories import RideshareProviderFactory, Car, MakeModel
from server.models import CarCompatibility

class TestCarCompatibility(TestCase):
    def setUp(self):
        self.delorean_2 = MakeModel.create(make='DMC', model='Delorean 2')

        self.uber_x = RideshareProviderFactory.create(name='uberX', friendly_id='uber_x')
        self.uber_x.compatible_models.add(self.delorean_2)

    def test_new_car(self):
        car = Car.create(year=2021, make_model=self.delorean_2)
        self.assertTrue(CarCompatibility(car).uber_x())

    def test_old_car(self):
        car = Car.create(year=1985, make_model=self.delorean_2)
        self.assertFalse(CarCompatibility(car).uber_x())
