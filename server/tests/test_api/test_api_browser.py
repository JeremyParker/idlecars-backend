# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from idlecars import production_settings, staging_settings
from server import factories

class ApiBrowserLocalTest(APITestCase):
    def test_api_root_auth(self):
        """
        Ensure we can browse root as a developer working locally
        """
        url = reverse('server:api-root')
        response = self.client.get(url, format='api')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_root_auth(self):
        """
        Ensure we can browse another API as a developer working locally
        """
        url = reverse('server:cars-list')
        response = self.client.get(url, format='api')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ApiBrowserProductionTest(APITestCase):
    def _login_staff(self):
        user = factories.StaffUser.create()
        self.client.login(username=user.username, password='mysecret')

    def test_api_root_production(self):
        """
        Ensure we can't browse root docs in production
        """
        self.assertFalse(
            'rest_framework.renderers.BrowsableAPIRenderer' in production_settings.REST_FRAMEWORK
        )
        with self.settings(REST_FRAMEWORK=production_settings.REST_FRAMEWORK):
            url = reverse('server:api-root')
            response = self.client.get(url, format='api')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_root_staging(self):
        """
        Ensure we can't browse root docs in staging
        """
        self.assertFalse(
            'rest_framework.renderers.BrowsableAPIRenderer' in staging_settings.REST_FRAMEWORK
        )
        with self.settings(REST_FRAMEWORK=staging_settings.REST_FRAMEWORK):
            url = reverse('server:api-root')
            response = self.client.get(url, format='api')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_car_json(self):
        """
        Ensure we CAN still access the car json in production
        """
        with self.settings(REST_FRAMEWORK=staging_settings.REST_FRAMEWORK):
            url = reverse('server:cars-list')
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            url = reverse('server:cars-detail', args=(100,))
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # not 403!

    def test_root_json_no_auth(self):
        """
        Ensure we can't access the root API in json if not authenticated
        """
        with self.settings(REST_FRAMEWORK=staging_settings.REST_FRAMEWORK):
            url = reverse('server:api-root')
            response = self.client.get(url, format='json')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_root_api_auth(self):
        """
        Just to make sure auth is working, check that we can access JSON if authenticated
        """
        self._login_staff()
        url = reverse('server:cars-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
