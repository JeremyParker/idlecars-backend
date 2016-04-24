# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories as server_factories
from owner_crm.tests import sample_merge_vars

from removal import models


class RemovalCreateTest(APITestCase):
    def setUp(self):
        self.owner = server_factories.Owner.create()

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('removal:removals-list')
        self.data = {'hack_license_number': '1234567'}

    def test_create_success(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['hack_license_number'], '1234567')

    def test_create_fail_not_logged_in(self):
        self.client.credentials()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class RemovalUpdateTest(APITestCase):
    def setUp(self):
        self.owner = server_factories.Owner.create()
        self.removal = models.Removal.objects.create(
            owner=self.owner,
            hack_license_number='1234567',
        )

        self.client = APIClient()
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_change_first_name(self):
        url = reverse('removal:removals-detail', args=(self.removal.pk,))
        response = self.client.patch(url, {'first_name': 'Marvin'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.removal.refresh_from_db()
        self.assertEqual(self.removal.first_name, 'Marvin')

    def test_change_last_name(self):
        url = reverse('removal:removals-detail', args=(self.removal.pk,))
        response = self.client.patch(url, {'last_name': 'Williams'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.removal.refresh_from_db()
        self.assertEquals(self.removal.last_name, 'Williams')

class RemovalNotificationTest(TestCase):
    def setUp(self):
        self.owner = server_factories.Owner.create()
        self.addition = models.Removal.objects.create(
            owner=self.owner,
        )

    def _fill_most_fields(self, addition):
        addition.first_name  = 'filled'
        addition.last_name  = 'filled'
        return addition

    def test_incomplete_sends_no_email(self):
        self.addition = self._fill_most_fields(self.addition)
        self.addition.save()
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_completion_sends_email(self):
        self.addition = self._fill_most_fields(self.addition)
        self.addition.hack_license_number = 'filled'
        self.addition.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))