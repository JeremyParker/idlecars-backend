# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from idlecars import fields

from server import factories
from server.models import Booking, Payment
from server import payment_gateways


class BookingCheckoutTest(APITestCase):
    def setUp(self):
        self.driver = factories.BaseLetterDriver.create()
        self.booking = factories.Booking.create(driver=self.driver)
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:bookings-checkout', args=(self.booking.pk,))

    def test_checkout_booking_success(self):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.booking.refresh_from_db()

        # the booking should be REQUESTED
        self.assertEqual(self.booking.get_state(), Booking.REQUESTED)

        # there should be one payment after checkout
        self.assertEqual(1, len(self.booking.payment_set.all()))

        # that payment should be pre-authorized
        self.assertEqual(self.booking.payment_set.first().status, Payment.PRE_AUTHORIZED)

    def test_cannot_checkout_booking_without_docs(self):
        self.booking.driver.defensive_cert_image = ''
        self.booking.driver.save()

        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data['_app_notifications'])  # it showed us an error.

    def test_checkout_payment_error(self):
        fake_gateway = payment_gateways.get_gateway('fake')
        fake_gateway.push_next_payment_response((Payment.DECLINED, 'Some fake error',))

        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data['_app_notifications'])  # it showed us an error.
