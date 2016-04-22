# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token


class TokenAuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='2121234567', password='password', email="idlecar@alltaxiny.com")
        self.url = reverse('server:token-auth')

    def test_user_with_valid_username_and_password_gets_auth_token(self):
        users_token = Token.objects.get(user_id=self.user.pk)
        expected_response = '"token":"{0}"'.format(users_token)
        response = self.client.post(self.url, {'username': '2121234567', 'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_response, response.content[1:-1])

    def test_user_with_invalid_username_and_password_does_not_get_auth_token(self):
        response = self.client.post(self.url, {'username': 'wrong', 'password': 'password'})
        expected_response = '{"non_field_errors":["Unable to log in with provided credentials."]}'
        self.assertEqual(response.status_code, 400)
        self.assertEqual(expected_response, response.content)

    def test_user_with_valid_username_and_invalid_password_does_not_get_auth_token(self):
        response = self.client.post(self.url, {'username': '2121234567', 'password': 'password1'})
        expected_response = '{"non_field_errors":["Unable to log in with provided credentials."]}'
        self.assertEqual(response.status_code, 400)
        self.assertEqual(expected_response, response.content)

    def test_user_with_invalid_username_and_valid_password_does_not_get_auth_token(self):
        response = self.client.post(self.url, {'username': '2121234666', 'password': 'password'})
        expected_response =  '{"non_field_errors":["Unable to log in with provided credentials."]}'
        self.assertEqual(response.status_code, 400)
        self.assertEqual(expected_response, response.content)
