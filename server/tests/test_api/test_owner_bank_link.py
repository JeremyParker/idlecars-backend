# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import copy

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories
from server import models


class BankLinkTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.owner = factories.AuthOwner.create()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.url = reverse('server:owners-bank-link', args=(self.owner.pk,))

    _fake_params = {
            'individual': {
                'first_name': "Jane",
                'last_name': "Doe",
                'email': "jane@14ladders.com",
                'phone': "5553334444",
                'date_of_birth': "1981-11-19",
                'ssn': "456-45-4567",
                'address': {
                    'street_address': "111 Main St",
                    'locality': "Chicago",
                    'region': "IL",
                    'postal_code': "60622"
                }
            },
            'business': {
                'legal_name': "Jane's Ladders",
                'dba_name': "Jane's Ladders",
                'tax_id': "98-7654321",
                'address': {
                    'street_address': "111 Main St",
                    'locality': "Chicago",
                    'region': "IL",
                    'postal_code': "60622"
                }
            },
            'funding': {
                'descriptor': "Blue Ladders",
                'email': "funding@blueladders.com",
                'mobile_phone': "5555555555",
                'account_number': "1123581321",
                'routing_number': "071101307",
            },
            "tos_accepted": True,
        }

    def test_merchant_id_added_to_owner(self):
        self.assertFalse(self.owner.merchant_id)
        response = self.client.post(self.url, self._fake_params, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reloaded_owner = models.Owner.objects.get(pk=self.owner.id)
        self.assertTrue(reloaded_owner.merchant_id)

    def test_fail_add_account_to_another(self):
        other_owner = factories.AuthOwner.create()
        self.assertFalse(other_owner.merchant_id)
        other_url = reverse('server:owners-bank-link', args=(other_owner.pk,))

        response = self.client.post(other_url, self._fake_params, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bad_params(self):
        # for testing, make tos_accepted = False
        params = copy.deepcopy(self._fake_params)
        params.update({ 'tos_accepted': False })

        response = self.client.post(self.url, params, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected = {
            "error_fields": ["tos_accepted"],
            "_app_notifications": ["Terms Of Service needs to be accepted. Applicant tos_accepted required."],
        }
        self.assertEqual(response.data, expected)
