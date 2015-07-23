# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server import serializers, factories, models

class TestCarCompatibilitySerializer(TestCase):
    def test_all_docs_uploaded_false(self):
        car = factories.Car.create()
        car_compatibility = models.CarCompatibility(car)
        serialized = serializers.CarCompatibilitySerializer(car_compatibility)
        self.assertEqual(serialized.data['uber_x'], 'uberX')
