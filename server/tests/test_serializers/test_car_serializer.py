# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase
from django.conf import settings
from django.utils import timezone

from server import serializers, factories
from server.models import Car


class TestCarSerializer(TestCase):
    def test_car_has_name(self):
        car = factories.Car.create()
        self.assertIsNotNone(serializers.CarSerializer(car).data['name'])
        self.assertTrue(car.make_model.make in serializers.CarSerializer(car).data['name'])
        self.assertTrue(car.make_model.model in serializers.CarSerializer(car).data['name'])

    def test_available_immediately(self):
        car = factories.Car.create(
            status='busy',
            next_available_date=timezone.now() - datetime.timedelta(days=1),
        )
        self.assertEqual(
            serializers.CarSerializer(car).data['available_date_display'],
            'Immediately',
        )

    def test_available_tomorrow(self):
        car = factories.Car.create(
            status='busy',
            next_available_date=timezone.now() + datetime.timedelta(days=1),
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

    def test_min_lease_unknown(self):
        car = factories.Car.create(min_lease='_00_unknown')
        self.assertEqual(serializers.CarSerializer(car).data['min_lease_display'], 'No minimum set')

    def test_min_lease_30(self):
        car = factories.Car.create(min_lease='_05_one_month')
        self.assertEqual(serializers.CarSerializer(car).data['min_lease_display'], '30 days')


class TextCarState(TestCase):
    def test_data_incomplete(self):
        car = factories.Car.create()
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Waiting for information')
        self.assertEqual(0, len(serializer_data['state_buttons']))
        # TODO - put this back in when the client can go to required field
        # self.assertEqual(1, len(serializer_data['state_buttons']))
        # self.assertEqual(serializer_data['state_buttons'][0]['label'], 'Complete this listing')
        # self.assertEqual(serializer_data['state_buttons'][0]['function_key'], 'GoRequiredField')

    def test_no_bank_deets(self):
        car = factories.ClaimedCar.create(status=Car.STATUS_AVAILABLE)
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Waiting for direct deposit information')
        self.assertEqual(1, len(serializer_data['state_buttons']))
        self.assertEqual(serializer_data['state_buttons'][0]['label'], 'Add bank details')
        self.assertEqual(serializer_data['state_buttons'][0]['function_key'], 'AddBankLink')

    def test_bank_pending_available(self):
        owner = factories.PendingOwner.create()
        car = factories.ClaimedCar.create(
            owner=owner,
            next_available_date=timezone.now(),
        )
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Waiting for bank account approval.')
        self.assertEqual(1, len(serializer_data['state_buttons']))
        self.assertEqual(serializer_data['state_buttons'][0]['label'], 'Remove listing')
        self.assertEqual(serializer_data['state_buttons'][0]['function_key'], 'RemoveListing')

    def test_bank_pending_busy(self):
        owner = factories.PendingOwner.create()
        car = factories.ClaimedCar.create(
            owner=owner,
            next_available_date=None,
        )
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Not listed.')
        self.assertEqual(1, len(serializer_data['state_buttons']))
        self.assertEqual(serializer_data['state_buttons'][0]['label'], 'List this car')
        self.assertEqual(serializer_data['state_buttons'][0]['function_key'], 'Relist')

    def test_reserved(self):
        car = factories.BookableCar.create()
        booking = factories.RequestedBooking.create(car=car)

        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Booked. Waiting for insurance approval.')
        self.assertEqual(1, len(serializer_data['state_buttons']))
        # TODO - hook up an API for approving/rejecting insurance, and put these buttons in to access it.
        # self.assertEqual(serializer_data['state_buttons'][0]['label'], 'The driver is approved')
        # self.assertEqual(serializer_data['state_buttons'][0]['function_key'], 'ApproveInsurance')
        # self.assertEqual(serializer_data['state_buttons'][1]['label'], 'The driver was rejected from the insurance')
        # self.assertEqual(serializer_data['state_buttons'][1]['function_key'], 'RejectInsurance')
        self.assertEqual(serializer_data['state_buttons'][0]['label'], 'This car is no longer available')
        self.assertEqual(serializer_data['state_buttons'][0]['function_key'], 'RemoveListing')

    def test_accepted(self):
        car = factories.BookableCar.create()
        booking = factories.AcceptedBooking.create(car=car)
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Booked. The driver will contact you to arrange pickup.')
        self.assertEqual(0, len(serializer_data['state_buttons']))

    def test_active_booking(self):
        car = factories.BookableCar.create()
        end_time = timezone.now() + datetime.timedelta(days=7)
        booking = factories.BookedBooking.create(car=car, end_time=end_time)
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Rented until {}'.format(end_time.strftime('%b %d')))
        self.assertEqual(0, len(serializer_data['state_buttons']))

    def test_busy(self):
        car = factories.BookableCar.create(next_available_date=None)
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Not listed.')
        self.assertEqual(1, len(serializer_data['state_buttons']))
        self.assertEqual(serializer_data['state_buttons'][0]['label'], 'List this car')
        self.assertEqual(serializer_data['state_buttons'][0]['function_key'], 'Relist')

    def test_stale(self):
        car = factories.BookableCar.create(
            last_status_update=timezone.now() - datetime.timedelta(days=settings.STALENESS_LIMIT+1)
        )
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(serializer_data['state_string'], 'Listing expired.')
        self.assertEqual(1, len(serializer_data['state_buttons']))
        self.assertEqual(serializer_data['state_buttons'][0]['label'], 'Extend this listing')
        self.assertEqual(serializer_data['state_buttons'][0]['function_key'], 'RenewListing')

    def test_available_way_future(self):
        future = timezone.now() + datetime.timedelta(days=90)
        car = factories.BookableCar.create(next_available_date=future)
        serializer_data = serializers.CarSerializer(car).data
        self.assertEqual(
            'Not listed. Busy until {}.'.format(future.strftime('%b %d')),
            serializer_data['state_string']
        )
        self.assertEqual(2, len(serializer_data['state_buttons']))
        self.assertEqual(serializer_data['state_buttons'][0]['label'], 'List this car')
        self.assertEqual(serializer_data['state_buttons'][0]['function_key'], 'Relist')
        self.assertEqual(serializer_data['state_buttons'][1]['label'], 'Change availability')
        self.assertEqual(serializer_data['state_buttons'][1]['function_key'], 'GoNextAvailableDate')

    def test_available_tomorrow(self):
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        car = factories.BookableCar.create(next_available_date=tomorrow)
        serializer_data = serializers.CarSerializer(car).data

        expiration_date = car.last_status_update + datetime.timedelta(days=settings.STALENESS_LIMIT)
        self.assertEqual(
            'Listed. This listing expires {}'.format(expiration_date.strftime('%b %d')),
            serializer_data['state_string']
        )
        self.assertEqual(2, len(serializer_data['state_buttons']))
        self.assertEqual(serializer_data['state_buttons'][0]['label'], 'Extend this listing')
        self.assertEqual(serializer_data['state_buttons'][0]['function_key'], 'RenewListing')
        self.assertEqual(serializer_data['state_buttons'][1]['label'], 'Remove listing')
        self.assertEqual(serializer_data['state_buttons'][1]['function_key'], 'RemoveListing')
