# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from rest_framework import status

class ExistsTest(TestCase):
    def test_endpoint_doesnt_exist(self):
        response = self.client.get('/e2e_test_setup')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
