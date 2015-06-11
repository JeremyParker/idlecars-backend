# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from server import factories, models


class DriverUpdateTest(APITestCase):
    def setUp(self):
        self.driver = factories.Driver.create()
        self.url = reverse('server:drivers-detail', args=(self.driver.id,))
        factories.UserAccount.create(driver=self.driver)

    def test_update_user_account_field(self):
        response = APIClient().patch(self.url, {'phone_number': 'newphone'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._driver_reloaded().phone_number(), 'newphone')

    def test_update_image_field(self):
        self.assertEqual(self.driver.driver_license_image, '')

        response = APIClient().patch(self.url, {'driver_license_image': 'newurl'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._driver_reloaded().driver_license_image, 'newurl')

    def _driver_reloaded(self):
        return models.Driver.objects.get(id=self.driver.id)
