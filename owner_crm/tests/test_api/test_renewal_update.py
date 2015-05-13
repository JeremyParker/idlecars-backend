# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils.six import BytesIO

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.test import APITestCase

from owner_crm import factories, models


class RenewalUpdateTest(APITestCase):
    def setUp(self):
        owner = factories.Renewal.create()

    def test_update_state(self):
        url = reverse('owner_crm:renewal-update')

        self.assertEqual(url, 'expected')
