# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib import auth

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from idlecars import fields
from server import factories, models


class AuthenticatedDriverTest(APITestCase):
    def setUp(self):
        self.driver = factories.Driver.create()

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:drivers-detail', args=(self.driver.id,))


class DriverRetrieveTest(AuthenticatedDriverTest):
    def _test_successful_get(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for k, v in response.data.iteritems():
            driver_val = getattr(self.driver, k)
            if callable(driver_val):
                driver_val = driver_val()
            if k == 'phone_number':
                driver_val = fields.format_phone_number(driver_val)
            self.assertEqual(response.data[k], driver_val)

    def test_get_driver_as_me(self):
        response = self.client.get(self.url, {'pk': 'me'})
        self._test_successful_get(response)

    def test_get_driver_by_id(self):
        response = self.client.get(self.url, {'pk': self.driver.pk})
        self._test_successful_get(response)

    def test_get_driver_fails_unauthorized(self):
        self.client.credentials()
        response = self.client.get(self.url, {'pk': 'me'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DriverUpdateTest(AuthenticatedDriverTest):
    def test_update_incomplete_model(self):
        # set up a driver with nothing more than phone number and password
        auth_user = auth.models.User.objects.create(username='1112223333')
        auth_user.set_password('test_pass')
        driver = models.Driver.objects.create(auth_user=auth_user)

        self.client = APIClient()
        token = Token.objects.get(user__username=driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:drivers-detail', args=(driver.id,))

        response = self.client.patch(self.url, {'email': 'test@testing.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        driver_reloaded = models.Driver.objects.get(id=driver.id)
        self.assertEqual(driver_reloaded.email(), 'test@testing.com')

    def test_update_username_field(self):
        response = self.client.patch(self.url, {'phone_number': '123 555 1212'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._driver_reloaded().phone_number(), '1235551212')

    def test_update_username_with_full_me(self):
        data = {
            'address_proof_image': "",
            'all_docs_uploaded': False,
            'client_display': "1112220987",
            'defensive_cert_image': "",
            'driver_license_image': "",
            'email': "",
            'fhv_license_image': "",
            'first_name': "",
            'id': 201,
            'last_name': "",
           ' phone_number': "(111) 222-3333",
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._driver_reloaded().phone_number(), '1112223333')

    def test_update_password_forbidden(self):
        response = self.client.patch(self.url, {'password': 'new_password'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check that the old password still works
        self.client.credentials()
        result = self.client.login(username=self.driver.phone_number(), password='password')
        self.assertTrue(result)

    def test_update_image_field(self):
        self.assertEqual(self.driver.driver_license_image, '')
        response = self.client.patch(self.url, {'driver_license_image': 'newurl'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._driver_reloaded().driver_license_image, 'newurl')

    def test_fails_when_not_owner(self):
        other_driver = factories.Driver.create()
        url = reverse('server:drivers-detail', args=(other_driver.id,))
        response = self.client.patch(url, {'driver_license_image': 'newurl'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fails_when_logged_out(self):
        self.client.credentials()
        response = self.client.patch(self.url, {'driver_license_image': 'newurl'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _driver_reloaded(self):
        return models.Driver.objects.get(id=self.driver.id)


class DriverCreateTest(APITestCase):
    def setUp(self):
        self.url = reverse('server:drivers-list')

    def test_create_driver(self):
        data = {'phone_number': '212 413 1234', 'password': 'test'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['phone_number'], '(212) 413-1234')
        self.assertFalse('password' in response.data)

        stored_phone_number = ''.join([n for n in response.data['phone_number'] if n.isdigit()])

        # check that it was created in the db
        new_driver = models.Driver.objects.get(auth_user__username=stored_phone_number)
        self.assertIsNotNone(new_driver)

        #check that the password works
        self.client.logout()
        self.assertTrue(self.client.login(username=stored_phone_number, password='test'))

    def test_create_driver_fails_with_existing_auth_user(self):
        self.auth_user = factories.AuthUser.create()

        self.client = APIClient()
        data = {'phone_number': self.auth_user.username, 'password': 'new_password'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_fails_with_no_password(self):
        data = {'phone_number': '212-413-1234'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_fails_with_no_phone(self):
        data = {'password': 'test'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
