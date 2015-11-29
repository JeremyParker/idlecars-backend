# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase
from django.utils import timezone

from server import serializers, factories
from server.models import Car


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


class TextCarState(TestCase):
    def test_data_incomplete(self):
        car = factories.Car.create()
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Waiting for information')
        self.assertEqual(serializer_data['state_cta_string'], 'Complete this listing')
        self.assertEqual(serializer_data['state_cta_key'], 'GoRequiredField')

    def test_busy_next_available(self):
        tomorrow = timezone.now().date() + datetime.timedelta(days=1)
        car = factories.ClaimedCar.create(
            status=Car.STATUS_BUSY,
            next_available_date=tomorrow,
        )
        serializer_data = serializers.CarSerializer(car).data
        self.assertTrue('Busy until' in serializer_data['state_string'])
        self.assertEqual(serializer_data['state_cta_string'], 'Change available date')
        self.assertEqual(serializer_data['state_cta_key'], 'GoNextAvailableDate')

    def test_busy_not_available(self):
        tomorrow = timezone.now().date() + datetime.timedelta(days=1)
        car = factories.ClaimedCar.create(
            status=Car.STATUS_BUSY,
            next_available_date=None,
        )
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Not listed')
        self.assertEqual(serializer_data['state_cta_string'], 'Relist')
        self.assertEqual(serializer_data['state_cta_key'], 'GoNextAvailableDate')

    def test_no_bank_deets(self):
        car = factories.ClaimedCar.create(status=Car.STATUS_AVAILABLE)
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Waiting for direct deposit information')
        self.assertEqual(serializer_data['state_cta_string'], 'Add bank details')
        self.assertEqual(serializer_data['state_cta_key'], 'AddBankLink')

    def test_bank_pending(self):
        owner = factories.PendingOwner.create()
        car = factories.ClaimedCar.create(
            owner=owner,
            status=Car.STATUS_AVAILABLE,
        )
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Waiting for bank approval')
        self.assertEqual(serializer_data['state_cta_string'], 'Remove listing')
        self.assertEqual(serializer_data['state_cta_key'], 'RemoveListing')

    def test_bank_approved(self):
        car = factories.BookableCar.create()
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Listed')
        self.assertEqual(serializer_data['state_cta_string'], 'Remove listing')
        self.assertEqual(serializer_data['state_cta_key'], 'RemoveListing')

        # elif car.owner and car.owner.merchant_account_state == Owner.BANK_ACCOUNT_PENDING:
        #     return {
        #         'string': 'Waiting for bank approval',
        #         'cta_string': 'Remove listing',
        #         'cta_key': 'RemoveListing',
        #     }
        # elif booking_service.filter_reserved(car.booking_set.all()):
        #     return {
        #         'string': 'Waiting for insurance approval',
        #         'cta_string': '',#'The driver is approved',
        #         'cta_key': '',#'ApproveInsurance',
        #     }
        # elif booking_service.filter_accepted(car.booking_set.all()):
        #     return {
        #         'string': 'Ready to be picked up',
        #         'cta_string': '',#'Contact the driver',
        #         'cta_key': '',#'ContactDriver',
        #     }
        # elif booking_service.filter_active(car.booking_set.all()):
        #     b = booking_service.filter_active(car.booking_set.all()).first()
        #     return {
        #         'string': 'Rented until'.format(b.end_date.strftime('%b %d')),
        #         'cta_string': '',#'Contact the driver',
        #         'cta_key': '',#'ContactDriver',
        #     }
        # else:
        #     return {
        #         'string': None,
        #         'cta_string': None,
        #         'cta_key': None,
        #     }
