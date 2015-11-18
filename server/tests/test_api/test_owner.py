# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import copy

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from idlecars import fields
from server import factories
from server import models
from server import payment_gateways


class GetOwnerTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.owner =  factories.Owner.create()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:owners-detail', args=(self.owner.pk,))

    # def test_get_self(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.data['id'], self.owner.pk)
    #     self.assertEqual(
    #         response.data['auth_users'][0]['phone_number'],
    #         fields.format_phone_number(self.owner.auth_users.all()[0].username)
    #     )

    # def test_get_me(self):
    #     self.url = reverse('server:owners-detail', args=('me',))
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.data['id'], self.owner.pk)
    #     self.assertEqual(
    #         response.data['auth_users'][0]['phone_number'],
    #         fields.format_phone_number(self.owner.auth_users.all()[0].username)
    #     )

    # def test_get_me_no_owner(self):
    #     user = self.owner.auth_users.first()
    #     self.owner.delete()
    #     self.url = reverse('server:owners-detail', args=('me',))
    #     response = self.client.get(self.url)

    #     new_owner = models.Owner.objects.get(auth_users=user)
    #     self.assertEqual(response.data['id'], new_owner.pk)
    #     self.assertEqual(
    #         response.data['auth_users'][0]['phone_number'],
    #         fields.format_phone_number(user.username),
    #     )

    def test_get_another_owner(self):
        other_owner = factories.Owner.create()
        self.url = reverse('server:owners-detail', args=(other_owner.pk,))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OwnerCreateTest(APITestCase):
    def setUp(self):
        self.user =  factories.AuthUser.create()
        token = Token.objects.get(user__username=self.user.username)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.url = reverse('server:owners-list')

    def test_create_owner(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that it was created in the db
        new_owner = models.Owner.objects.get(auth_users=self.user)
        self.assertIsNotNone(new_owner)

        # make sure our user is among the users
        self.assertTrue(self.user.pk in [u['id'] for u in response.data['auth_users']])


class BankLinkTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.owner =  factories.Owner.create()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.url = reverse('server:owners-bank-link', args=(self.owner.pk,))

    def test_merchant_id_added_to_individual_owner(self):
        self.assertFalse(self.owner.merchant_id)
        response = self.client.post(
            self.url,
            payment_gateways.test_braintree_params.individual_data['from_client'],
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reloaded_owner = models.Owner.objects.get(pk=self.owner.id)
        self.assertTrue(reloaded_owner.merchant_id)
        try:
            self.assertDictEqual(
                payment_gateways.get_gateway('fake').most_recent_request_data,
                payment_gateways.test_braintree_params.individual_data['to_braintree']
            )
        except AssertionError as e:
            print 'Maybe you\'re running this test with settings set to use braintree gateway?'
            raise e

    def test_merchant_id_added_to_business_owner(self):
        self.assertFalse(self.owner.merchant_id)
        response = self.client.post(
            self.url,
            payment_gateways.test_braintree_params.business_data['from_client'],
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reloaded_owner = models.Owner.objects.get(pk=self.owner.id)
        self.assertTrue(reloaded_owner.merchant_id)
        try:
            self.assertDictEqual(
                payment_gateways.get_gateway('fake').most_recent_request_data,
                payment_gateways.test_braintree_params.business_data['to_braintree']
            )
        except AssertionError as e:
            print 'Maybe you\'re running this test with settings set to use braintree gateway?'
            raise e

    def test_fail_add_account_to_another(self):
        other_owner =  factories.Owner.create()
        self.assertFalse(other_owner.merchant_id)
        other_url = reverse('server:owners-bank-link', args=(other_owner.pk,))
        response = self.client.post(
            other_url,
            payment_gateways.test_braintree_params.individual_data['from_client'],
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bad_params(self):
        # for testing, make tos_accepted = False
        params = copy.deepcopy(payment_gateways.test_braintree_params.individual_data['from_client'])
        params.update({ 'tos_accepted': False })

        response = self.client.post(self.url, params, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected = {
            "error_fields": ["tos_accepted"],
            "_app_notifications": [
                "Terms Of Service needs to be accepted. Applicant tos_accepted required.",
            ],
        }
        self.assertEqual(response.data, expected)
