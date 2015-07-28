# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server import serializers, factories, models

class TestCarCompatibilitySerializer(TestCase):
    def setUp(self):
        uber_x = factories.RideshareFlavorFactory.create(friendly_id='uber_x', name='TacoRide')
        car = factories.Car.create(year=2222)
        uber_x.compatible_models.add(car.make_model)
        self.car_compatibility = models.CarCompatibility(car)

    # PENDING: implementation of comaptibility logic

    # def test_serializer(self):
    #     serialized = serializers.CarCompatibilitySerializer(self.car_compatibility)
    #     self.assertEqual(serialized.data['uber_x'], 'TacoRide')
