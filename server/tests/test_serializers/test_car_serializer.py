# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase
from django.utils import timezone

from server import serializers, factories


class TestCarSerializer(TestCase):
    def test_car_has_name(self):
        car = factories.Car.create()
        self.assertIsNotNone(serializers.CarSerializer(car).data['name'])
        self.assertTrue(car.make_model.make in serializers.CarSerializer(car).data['name'])
        self.assertTrue(car.make_model.model in serializers.CarSerializer(car).data['name'])

    def test_available_immediately2(self):
        car = factories.Car.create(
            status='available',
        )
        self.assertEqual(
            serializers.CarSerializer(car).data['available_date_display'],
            'Immediately',
        )

    def test_available_immediately(self):
        car = factories.Car.create(
            status='busy',
            next_available_date=timezone.now().date() - datetime.timedelta(days=1),
        )
        self.assertEqual(
            serializers.CarSerializer(car).data['available_date_display'],
            'Immediately',
        )

    def test_available_tomorrow(self):
        car = factories.Car.create(
            status='busy',
            next_available_date=timezone.now().date() + datetime.timedelta(days=1),
        )
        self.assertEqual(
            serializers.CarSerializer(car).data['available_date_display'],
            car.next_available_date.strftime('%b %d'),
        )

    def test_not_available(self):
        car = factories.Car.create(
            status='busy',
        )
        self.assertEqual(
            serializers.CarSerializer(car).data['available_date_display'],
            'Unavailable',
        )
