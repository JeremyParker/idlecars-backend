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
        self.assertEqual([self.uber_x.name], CarCompatibility(car).all())

    def test_non_compatible_model(self):
        car = Car.create(make_model=self.non_compaitble)
        self.assertEqual([], CarCompatibility(car).all())


class TestLyft(TestCase):
    def setUp(self):
        self.lyft_standard = RideshareFlavorFactory.create(name='Lyft', friendly_id='lyft_standard')
        self.lyft_plus = RideshareFlavorFactory.create(name='Lyft Plus', friendly_id='lyft_plus')

    def test_lil_car(self):
        mm = MakeModel.create(passenger_count=2)
        car = Car.create(make_model=mm)
        self.assertEqual([self.lyft_standard.name], CarCompatibility(car).all())

    def test_big_car(self):
        mm = MakeModel.create(passenger_count=22)
        car = Car.create(make_model=mm)
        self.assertEqual([self.lyft_plus.name], CarCompatibility(car).all())


class TestGett(TestCase):
    def setUp(self):
        self.gett_standard = RideshareFlavorFactory.create(name='Gett', friendly_id='gett_standard')

    def test_black_on_black(self):
        car = Car.create(exterior_color=0, interior_color=0)
        self.assertEqual([self.gett_standard.name], CarCompatibility(car).all())

    def test_black_on_blue(self):
        car = Car.create(exterior_color=0, interior_color=3)
        self.assertEqual([], CarCompatibility(car).all())

    def test_blue_on_black(self):
        car = Car.create(exterior_color=4, interior_color=0)
        self.assertEqual([], CarCompatibility(car).all())
