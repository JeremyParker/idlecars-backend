# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories, models


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
        self.assertEqual(response.data['detail'], 'You already have a booking in progress.')


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
            self.assertEqual(booking_data['driver'], self.driver.pk)

    def test_get_booking_list_one_pending_one_booked(self):
        self.booking.status = models.Booking.BOOKED
        booking2 = factories.Booking.create(driver=self.driver, state=models.Booking.PENDING)

        response = self.client.get(self.url, format='json') 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for booking_data in response.data:
            self.assertEqual(booking_data['driver'], self.driver.pk)
