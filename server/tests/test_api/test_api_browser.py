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
