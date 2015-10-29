# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import serializers, factories


class TestBookingSerializer(APITestCase):
    def test_after_checkout(self):
        booking = factories.BookedBooking.create()

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=booking.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('server:bookings-list')
        response = self.client.get(url, format='json')

        self.assertIsNotNone(response.data[0]['paid_payments'][0])
        payment = response.data[0]['paid_payments'][0]
        self.assertEqual(decimal.Decimal(payment['amount']),  booking.weekly_rent)
        self.assertEqual(payment['status'],  'paid')
