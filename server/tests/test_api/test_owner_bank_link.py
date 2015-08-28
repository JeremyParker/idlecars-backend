# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
# from rest_framework.authtoken.models import Token

from server import factories


class BankLinkTest(APITestCase):
    def setUp(self):
        self.owner = factories.Owner.create()
        self.client = APIClient()
        self.url = reverse('server:owners-bank-link', args=(self.owner.pk,))

    def test_merchant_id_added_to_owner(self):
        self.assertFalse(self.owner.merchant_id)
        response = self.client.post(self.url, self._fake_params(), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.owner.merchant_id)

    def _fake_params(self):
        return {
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

