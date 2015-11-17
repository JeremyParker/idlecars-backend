# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from idlecars import fields
from server import factories

test_email = "idlecar@idlecars.com"

class UserApiTest(APITestCase):
    def setUp(self):
        self.user = factories.AuthUser.create(username='2121234567', password='password', email=test_email)
        token = Token.objects.get(user__username=self.user.username)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:users-detail', args=(self.user.id,))

    def test_get_me(self):
        response = self.client.get(self.url, {'pk': 'me'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        formatted_phone = fields.format_phone_number(self.user.username)
        self.assertEqual(response.data['phone_number'], formatted_phone)
        self.assertEqual(response.data['email'], test_email)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)

    def test_cannot_get_other_user(self):
        other_user = factories.AuthUser.create()
        url = reverse('server:users-detail', args=(other_user.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
