# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from server import factories, models


class DriverUpdateTest(APITestCase):
    def setUp(self):
        self.driver = factories.Driver.create()
        self.original_phone = self.driver.phone_number

    def test_update_state(self):
        url = reverse('server:drivers-detail', args=(self.driver.id,))
        response = APIClient().patch(url, {'phone_number': 'newphone'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._assert_updated()

    def _assert_updated(self):
        driver = models.Driver.objects.get(id=self.driver.id)
        self.assertEqual(driver.phone_number, 'newphone')
