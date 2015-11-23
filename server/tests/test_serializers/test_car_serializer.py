# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server import serializers, factories

class TestCarSerializer(TestCase):
    def test_car_has_name(self):
        car = factories.Car.create()
        self.assertIsNotNone(serializers.CarSerializer(car).data['name'])
        self.assertTrue(car.make_model.make in serializers.CarSerializer(car).data['name'])
        self.assertTrue(car.make_model.model in serializers.CarSerializer(car).data['name'])
