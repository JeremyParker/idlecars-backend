# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
import decimal
from braintree.test.nonces import Nonces

from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories, models, services


class CreateBookingTest(APITestCase):
    def setUp(self):
        self.car = factories.BookableCar.create()
        self.driver = factories.Driver.create()

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:bookings-list')
        self.data = {'car': str(self.car.pk)}

    def test_create_booking_success(self):
        """ Ensure we can create a new booking object. """
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['car'], self.car.pk)
        self.assertEqual(response.data['driver'], self.driver.pk)

    def test_create_booking_fail_not_logged_in(self):
        """ Ensure we can't book if not logged in"""
        self.client.credentials()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fail_when_car_is_booked(self):
        other_driver = factories.CompletedDriver.create()
        existing_booking = factories.RequestedBooking.create(car=self.car, driver=other_driver)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['_app_notifications'], [services.booking.UNAVAILABLE_CAR_ERROR])

    def test_fail_when_driver_has_pending_booking(self):
        """ Ensure we can't book if the driver already has an oustanding PENDING booking"""
        other_car = factories.Car.create()
        existing_booking = factories.Booking.create(car=other_car, driver=self.driver)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['_app_notifications'], ['You have a conflicting rental.'])

    def test_fail_when_driver_has_booked_booking(self):
        other_car = factories.BookableCar.create()
        existing_booking = factories.ReturnedBooking.create(car=other_car, driver=self.driver)
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['_app_notifications'], ['You have a conflicting rental.'])

    def test_success_when_driver_has_canceled_booking(self):
        other_car = factories.Car.create()
        existing_booking = factories.IncompleteBooking.create(
            car=other_car,
            driver=self.driver,
            requested_time=timezone.now(),
            checkout_time=timezone.now(),
        )
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['car'], self.car.pk)
        self.assertEqual(response.data['driver'], self.driver.pk)


class ListBookingTest(APITestCase):
    def setUp(self):
        self.driver = factories.Driver.create()
        self.booking = factories.Booking.create(driver=self.driver)

        # populate the db with a bunch of bookings not related to this driver
        for i in range(10):
            factories.Booking.create()

        # Include an appropriate `Authorization:` header on all requests.
        self.client = APIClient()
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:bookings-list')

    def test_get_booking_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        for booking_data in response.data:
            self.assertEqual(booking_data['car']['id'], self.booking.car.pk)

    def test_get_booking_list_one_pending_one_booked(self):
        booking2 = factories.ReturnedBooking.create(driver=self.driver)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        ids = [b['car']['id'] for b in response.data]
        self.assertTrue(booking2.car.pk in ids)
        self.assertTrue(self.booking.car.pk in ids)

    def test_canceled_booking_excluded(self):
        self.booking.incomplete_time = timezone.now()
        self.booking.incomplete_reason = models.Booking.REASON_CANCELED
        self.booking.save()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class BookingStepTest(APITestCase):
    '''
    Test that the booking shows the correct steps at the correct times as it
    transitions through all states
    '''
    def setUp(self):
        self.car = factories.BookableCar.create()

    def _setup_client(self):
        self.client = APIClient()
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = self.client.post(
            reverse('server:bookings-list'),
            data={'car': self.car.pk, 'driver': self.driver.pk},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.booking = models.Booking.objects.get(pk=response.data['id'])
        self.url = reverse('server:bookings-detail', args=(self.booking.pk,))

    def test_new_driver_starts(self):
        self.driver = factories.Driver.create()
        self._setup_client()
        self._pending_no_docs()

    def _pending_no_docs(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.data['step'], 2)

        # driver completes their account
        self.driver.ssn = '123456789'
        self.driver.driver_license_image = 'some image'
        self.driver.fhv_license_image = 'some image'
        self.driver.address_proof_image = 'some image'
        self.driver.defensive_cert_image = 'some image'
        self.driver.save()
        self._requested()

    def test_complete_driver_starts(self):
        self.driver = factories.CompletedDriver.create()
        self._setup_client()
        self._requested()

    def _requested(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['step'], 3)

        # next, the insurance gets accepted
        self.booking.approval_time = timezone.now()
        self.booking.save()
        self._in_progress_booking()

    def _in_progress_booking(self):
        # NOTE: state = RETURNED
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.data['step'], 4)
