# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from rest_framework import status

class ExistsTest(TestCase):
    def test_endpoint_doesnt_exist(self):
        '''
            This test ensures that you cannot access this endpoint
            It is only allowed when `idlecars.test_settings` are invoked
        '''
        response = self.client.get('/e2e_test_setup')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
