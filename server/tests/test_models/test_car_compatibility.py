# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server.factories import RideshareProviderFactory, Car, MakeModel
from server.models import CarCompatibility

class TestCarCompatibility(TestCase):
    def test_new_car(self):
        delorean_2 = MakeModel.create(make='DMC', model='Delorean 2')
        rideshare_provider = RideshareProviderFactory.create(name='uberX', frieldly_id='uber_x')
        rideshare_provider.compatible_models.add(delorean_2)
        new_car = Car.create(year=2021, make_model=delorean_2)

        self.assertTrue(CarCompatibility(new_car).uber_x())

