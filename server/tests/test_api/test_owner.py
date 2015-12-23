# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import copy

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from idlecars import fields
from idlecars.factories import AuthUser
from server import factories
from server import models
from server import payment_gateways


class GetOwnerNoAuthTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner =  factories.Owner.create()

    def test_get_me_unauthenticated(self):
        response = self.client.get(reverse('server:owners-detail', args=('me',)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_owner_unauthenticated(self):
        response = self.client.get(reverse('server:owners-detail', args=(self.owner.pk,)))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_unauthenticated(self):
        response = self.client.post(reverse('server:owners-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_unauthenticated(self):
        url = reverse('server:owners-detail', args=(self.owner.pk,))
        response = self.client.patch(url, {'company_name': 'bla'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetOwnerTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.owner =  factories.Owner.create()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:owners-detail', args=(self.owner.pk,))

    def test_get_self(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data['id'], self.owner.pk)
        self.assertEqual(
            response.data['auth_users'][0]['phone_number'],
            fields.format_phone_number(self.owner.auth_users.all()[0].username)
        )

    def test_get_me(self):
        self.url = reverse('server:owners-detail', args=('me',))
        response = self.client.get(self.url)
        self.assertEqual(response.data['id'], self.owner.pk)
        self.assertEqual(
            response.data['auth_users'][0]['phone_number'],
            fields.format_phone_number(self.owner.auth_users.all()[0].username)
        )

    def test_get_me_no_owner(self):
        user = self.owner.auth_users.first()
        self.owner.delete()
        self.url = reverse('server:owners-detail', args=('me',))
        response = self.client.get(self.url)

        new_owner = models.Owner.objects.get(auth_users=user)
        self.assertEqual(response.data['id'], new_owner.pk)
        self.assertEqual(
            response.data['auth_users'][0]['phone_number'],
            fields.format_phone_number(user.username),
        )

    def test_get_another_owner(self):
        other_owner = factories.Owner.create()
        self.url = reverse('server:owners-detail', args=(other_owner.pk,))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OwnerCreateTest(APITestCase):
    def setUp(self):
        self.user =  AuthUser.create()
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


class OwnerUpdateTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner =  factories.Owner.create()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:owners-detail', args=('me',))

    def test_update_incomplete_model(self):
        self.url = reverse('server:users-detail', args=(self.owner.auth_users.last().id,))
        # this is to reset email for testing on set email
        self.client.patch(self.url, {'email': ''}, format='json')

        response = self.client.patch(self.url, {'email': 'test@testing.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.owner.auth_users.last().refresh_from_db()
        self.assertEqual(self.owner.email(), 'test@testing.com')

        # TODO: we need to test this once we setup the owner signup email
        # from django.core.mail import outbox
        # self.assertEqual(len(outbox), 1)
        # self.assertEqual(outbox[0].subject, 'Welcome to Idlecars')

    def test_update_company_name(self):
        company_name = 'Miguel\'s Cars'
        response = self.client.patch(self.url, {'company_name': company_name}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], company_name)

    def test_cannot_update_another_owner(self):
        other_owner =  factories.Owner.create()
        other_url = reverse('server:owners-detail', args=(other_owner.pk,))
        response = self.client.patch(other_url, {'company_name': 'bla'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_me_with_no_owner_creates_owner(self):
        '''
        This is weird behavior, but we always support an authenticated user interacting
        with their Owner object as if they had always had an Owner object, even if they never did.
        '''
        self.owner.delete()
        response = self.client.patch(self.url, {'company_name': 'bla'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'bla')


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
