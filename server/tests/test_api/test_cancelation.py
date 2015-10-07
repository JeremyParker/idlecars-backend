# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from idlecars import fields

from server import factories
from server.models import Booking


class CancelBookingTest(APITestCase):
    def setUp(self):
        self.driver = factories.Driver.create()
        self.booking = factories.Booking.create(driver=self.driver)
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:bookings-cancelation', args=(self.booking.pk,))

    def test_cancel_booking_success(self):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.booking = Booking.objects.get(pk=self.booking.pk)
        self.assertEqual(self.booking.get_state(), Booking.INCOMPLETE)
        self.assertEqual(self.booking.incomplete_reason, Booking.REASON_CANCELED)

    def test_not_cancel_anothers_booking(self):
        another_booking = factories.Booking.create()
        url = reverse('server:bookings-cancelation', args=(another_booking.pk,))

        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_cancel_booked_booking(self):
        # set the booking to "Booked"
        self.booking = factories.BookedBooking.create(driver=self.driver)
        url = reverse('server:bookings-cancelation', args=(self.booking.pk,))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # make sure the stored booking state is the same as original booking state
        stored_booking = Booking.objects.get(pk=self.booking.pk)
        self.assertEqual(stored_booking.get_state(), self.booking.get_state())
