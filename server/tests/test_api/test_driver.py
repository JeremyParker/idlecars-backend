# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils.six import BytesIO

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from server import factories, models


class DriverUpdateTest(APITestCase):
    def setUp(self):
        self.driver = factories.Driver.create()

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:drivers-detail', args=(self.driver.id,))

    def test_update_auth_user_field(self):
        response = self.client.patch(self.url, {'phone_number': 'newphone'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._driver_reloaded().phone_number(), 'newphone')

    def test_update_password(self):
        response = self.client.patch(self.url, {'password': 'new_password'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials()
        result = self.client.login(username=self.driver.phone_number(), password='new_password')
        self.assertTrue(result)

    def test_update_image_field(self):
        self.assertEqual(self.driver.driver_license_image, '')
        response = self.client.patch(self.url, {'driver_license_image': 'newurl'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._driver_reloaded().driver_license_image, 'newurl')

    def test_fails_when_logged_out(self):
        self.client.logout()  # we have to call logout in test too, because 
        self.client.credentials()
        response = self.client.patch(self.url, {'driver_license_image': 'newurl'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _driver_reloaded(self):
        return models.Driver.objects.get(id=self.driver.id)


class DriverCreateTest(APITestCase):
    def setUp(self):
        self.url = reverse('server:drivers-list')

    def test_create_driver(self):
        data = {'phone_number': '212-413-1234', 'password': 'test'}
        response = APIClient().post(self.url, data)
        stream = BytesIO(response.content)
        response_data = JSONParser().parse(stream)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_data['phone_number'], data['phone_number'])
        self.assertFalse('password' in response_data)

        # check that it was created in the db
        new_driver = models.Driver.objects.get(auth_user__username=response_data['phone_number'])
        self.assertIsNotNone(new_driver)

        #check that the password works
        self.client.logout()
        self.assertTrue(self.client.login(username='212-413-1234', password='test'))

    def test_create_driver_fails_with_no_password(self):
        data = {'phone_number': '212-413-1234'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_fails_with_no_phone(self):
        data = {'password': 'test'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DriverGetTest(APITestCase):
    def setUp(self):
        pass
