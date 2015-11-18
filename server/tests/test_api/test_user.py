# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

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
        self.url = reverse('server:users-detail', args=('me',))

    def test_get_me(self):
        response = self.client.get(self.url)
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

    def test_update_email(self):
        response = self.client.patch(self.url, {'email': 'test@testing.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_reloaded = User.objects.get(pk=self.user.pk)
        self.assertEqual(user_reloaded.email, 'test@testing.com')

    def test_update_first_name(self):
        response = self.client.patch(self.url, {'first_name': 'Mikey'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_reloaded = User.objects.get(pk=self.user.pk)
        self.assertEqual(user_reloaded.first_name, 'Mikey')

    def test_update_last_name(self):
        response = self.client.patch(self.url, {'last_name': 'McCarthy'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_reloaded = User.objects.get(pk=self.user.pk)
        self.assertEqual(user_reloaded.last_name, 'McCarthy')

    def test_cannot_update_someone_else(self):
        other_user = factories.AuthUser.create()
        url = reverse('server:users-detail', args=(other_user.id,))
        response = self.client.patch(url, {'first_name': 'Mikey'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_update_password(self):
        url = reverse('server:users-detail', args=(self.user.id,))
        response = self.client.patch(url, {'password': 'other_password'})
        self.assertTrue(self.user.check_password('password'))
        self.assertEqual(response.status_code, status.HTTP_200_OK) # it doesn't update

    def test_user_with_driver_returns_driver(self):
        driver = factories.Driver.create(auth_user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['driver'], driver.pk)

    def test_user_with_owner_returns_owner(self):
        owner = factories.Owner.create()
        owner.auth_users.add(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner'], owner.pk)

    def test_owner_driver_returns_both(self):
        driver = factories.Driver.create(auth_user=self.user)
        owner = factories.Owner.create()
        owner.auth_users.add(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner'], owner.pk)
        self.assertEqual(response.data['driver'], driver.pk)


class UserCreateTest(APITestCase):
    def setUp(self):
        self.url = reverse('server:users-list')

    def test_create_user(self):
        data = {'phone_number': '212 413 1234', 'password': 'test'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['phone_number'], '(212) 413-1234')
        self.assertFalse('password' in response.data)

        stored_phone_number = ''.join([n for n in response.data['phone_number'] if n.isdigit()])

        # check that it was created in the db
        new_user = User.objects.get(username=stored_phone_number)
        self.assertIsNotNone(new_user)

        #check that the password works
        self.client.logout()
        self.assertTrue(self.client.login(username=stored_phone_number, password='test'))

    def test_create_fails_with_existing_user(self):
        existing_user = factories.AuthUser.create()
        data = {'phone_number': existing_user.username, 'password': 'new_password'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_fails_with_no_password(self):
        data = {'phone_number': '212-413-1234'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_fails_with_no_phone(self):
        data = {'password': 'test'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
