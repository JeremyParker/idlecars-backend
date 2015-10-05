# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from idlecars import fields

from server import factories, models


class OwnerPhoneNumberTest(APITestCase):
    def setUp(self):
        self.owner = factories.Owner.create()

    # they already signed up, they should just log in
    def test_owner_and_user(self):
        phone_number = self.owner.auth_users.latest('pk').username
        url = reverse('server:owner_phone_numbers', args=(phone_number,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['phone_number'],
            fields.format_phone_number(phone_number),
        )
        self.assertNotIn('_app_notifications', response.data.keys())

    # owner who mistakenly signed up as driver first
    def test_driver_and_owner(self):
        driver = factories.Driver.create()
        url = reverse('server:owner_phone_numbers', args=(driver.phone_number(),))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # no user account yet
    def test_wrong_number(self):
        url = reverse('server:owner_phone_numbers', args=('6663334444',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
