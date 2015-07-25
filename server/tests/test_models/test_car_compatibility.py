# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server import factories
from server.models import CarCompatibility

class TestCarCompatibility(TestCase):
    def test_new_car(self):
        make_model = factories.MakeModel.create(make='DMC', model='Delorean 2')
        rideshare_provider = factories.RideshareProvider.create(name='uberX', frieldly_id='uber_x')
        new_car = factories.Car.create(year=2021)

        self.assertTrue(CarCompatibility(new_car).uber_x())

