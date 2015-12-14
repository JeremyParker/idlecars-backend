# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from idlecars import fields

from server import factories
from server.services import invoice_service
from server.services import booking as booking_service
from server.models import Booking, Payment
from server import payment_gateways


class BookingPickupTest(APITestCase):
    def setUp(self):
        self.driver = factories.BaseLetterDriver.create()
        self.booking = factories.AcceptedBooking.create(driver=self.driver)
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:bookings-pickup', args=(self.booking.pk,))

    def test_pickup_booking_success(self):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # the booking should be ACTIVE in the db
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.get_state(), Booking.ACTIVE)

        # booking should be in step "5"
        self.assertEqual(response.data['step'], 5)

        # there should be two payments after pickup
        self.assertEqual(2, len(self.booking.payment_set.all()))

        # the deposit payment should be held in escrow
        deposit = invoice_service.find_deposit_payment(self.booking)
        self.assertEqual(deposit.status, Payment.HELD_IN_ESCROW)

        # the first week rent should be settled
        for p in self.booking.payment_set.all():
            if p.invoice_start_time:
                self.assertEqual(p.status, Payment.SETTLED)

    def test_cannot_pickup_not_approved(self):
        self.booking.approval_time = None
        self.booking.save()

        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data['_app_notifications'])  # it showed us an error.

    def test_checkout_payment_error(self):
        fake_gateway = payment_gateways.get_gateway('fake')
        fake_gateway.push_next_payment_response((Payment.DECLINED, 'Some fake error',))
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data['_app_notifications'])  # it showed us an error.
