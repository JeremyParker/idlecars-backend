# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from idlecars import fields
from idlecars.factories import AuthUser

from server import factories, models


class PhoneNumberTest(APITestCase):
    def setUp(self):
        self.driver = factories.Driver.create()
        self.owner = factories.Owner.create()
        self.user = AuthUser.create()

    def test_get_phone_number_success_driver(self):
        url = reverse('server:phone_numbers', args=(self.driver.phone_number(),))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['phone_number'],
            fields.format_phone_number(self.driver.phone_number())
        )

    def test_get_phone_number_success_owner(self):
        url = reverse('server:phone_numbers', args=(self.owner.phone_number(),))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['phone_number'],
            fields.format_phone_number(self.owner.phone_number())
        )

    def test_get_phone_number_success_user(self):
        url = reverse('server:phone_numbers', args=(self.user.username,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['phone_number'],
            fields.format_phone_number(self.user.username)
        )

    def test_get_phone_number_success_with_random_chars(self):
        num = self.driver.phone_number()
        whacky_phone_number = '(+{}) {}.{}-{}'.format(
            num[:1],
            num[1:3],
            num[3:5],
            num[5:10],
        )
        url = reverse('server:phone_numbers', args=(whacky_phone_number,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['phone_number'],
            fields.format_phone_number(self.driver.phone_number())
        )

    def test_get_phone_number_fails(self):
        url = reverse('server:phone_numbers', args=('123',))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
