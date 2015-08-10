# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories, models, services


class CreateBookingTest(APITestCase):
    def setUp(self):
        self.car = factories.Car.create()
        self.driver = factories.Driver.create()

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:bookings-list')
        self.data = {'car': self.car.pk}

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

    def test_create_booking_fail_when_driver_busy(self):
        """ Ensure we can't book if the driver already has an oustanding booking"""
        other_car = factories.Car.create()
        existing_booking = models.Booking.objects.create(car=other_car, driver=self.driver)
        existing_booking.state = models.Booking.COMPLETE
        existing_booking.save()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['_app_notifications'], ['You have a conflicting rental.'])


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
        self.booking.status = models.Booking.BOOKED
        booking2 = factories.Booking.create(driver=self.driver, state=models.Booking.PENDING)

        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        ids = [b['car']['id'] for b in response.data]
        self.assertTrue(booking2.car.pk in ids)
        self.assertTrue(self.booking.car.pk in ids)

    def test_canceled_booking_excluded(self):
        self.booking.state = models.Booking.CANCELED
        self.booking.save()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_cancelable_bookings(self):
        for state in services.booking.cancelable_states():
            self.booking.state = state
            self.booking.save()
            response = self.client.get(self.url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data[0]['state_details']['cancelable'])

        visible = services.booking.visible_states()
        cancelable = services.booking.cancelable_states()
        un_cancelable = [s for s in visible if s not in cancelable]

        for state in un_cancelable:
            self.booking.state = state
            self.booking.save()
            response = self.client.get(self.url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(response.data[0]['state_details']['cancelable'])


class UpdateBookingTest(APITestCase):
    def setUp(self):
        self.booking = factories.Booking.create(
            state=models.Booking.PENDING,
            end_time=datetime.datetime(2014, 12, 15, 14, tzinfo=timezone.get_current_timezone())
        )

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.booking.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:bookings-detail', args=(self.booking.pk,))

    def test_cancel_booking_success(self):
        data = { 'state': models.Booking.CANCELED }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking = models.Booking.objects.get(id=self.booking.pk)
        self.assertEqual(self.booking.state, models.Booking.CANCELED)

    def test_not_cancel_anothers_booking(self):
        another_booking = factories.Booking.create()
        data = { 'state': models.Booking.CANCELED }
        url = reverse('server:bookings-detail', args=(another_booking.pk,))
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_set_booking_to_non_cancel(self):
        data = { 'state': models.Booking.BOOKED }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_cancel_booked_booking(self):
        # set the booking to "Booked"
        self.booking.state = models.Booking.BOOKED
        self.booking.save()

        data = { 'state': models.Booking.CANCELED }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_end_time(self):
        data = {'end_time': [2015, 0, 1]}  # happy new year
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking = models.Booking.objects.get(id=self.booking.pk)
        expected_end = datetime.datetime(2015, 1, 1, tzinfo=timezone.get_current_timezone())
        self.assertEqual(
            self.booking.end_time.astimezone(timezone.get_current_timezone()),
            expected_end
        )
