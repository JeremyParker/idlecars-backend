# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories as server_factories
from owner_crm.tests import sample_merge_vars

from addition import models


class AdditionCreateTest(APITestCase):
    def setUp(self):
        self.owner = server_factories.Owner.create()

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('addition:additions-list')
        self.data = {'plate': '1A10'}

    def test_create_addition_success(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['plate'], '1A10')

    def test_create_addition_fail_not_logged_in(self):
        self.client.credentials()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class AdditionUpdateTest(APITestCase):
    def setUp(self):
        self.owner = server_factories.Owner.create()
        self.addition = models.Addition.objects.create(
            owner=self.owner,
            plate='REAL_MEDALLION',
        )

        self.client = APIClient()
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_change_addition_details(self):
        url = reverse('addition:additions-detail', args=(self.addition.pk,))
        response = self.client.patch(url, {'first_name': 'Marvin'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.addition.refresh_from_db()
        self.assertEqual(self.addition.first_name, 'Marvin')

    def test_authorize_mvr(self):
        url = reverse('addition:additions-detail', args=(self.addition.pk,))
        response = self.client.patch(url, {'mvr_authorized': None}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.addition.refresh_from_db()
        self.assertIsNotNone(self.addition.mvr_authorized)


class AdditionNotificationTest(TestCase):
    def setUp(self):
        self.owner = server_factories.Owner.create()

    def _fill_most_fields(self, addition):
        addition.phone_number = '1234567890'
        addition.first_name  = 'filled'
        addition.last_name  = 'filled'
        addition.ssn  = 'filled'
        addition.driver_license_image  = 'filled'
        addition.fhv_license_image = 'filled'
        return addition

    def test_incomplete_sends_no_email(self):
        self.addition = models.Addition.objects.create(
            owner=self.owner,
            plate='REAL_MEDALLION',
        )
        self.addition = self._fill_most_fields(self.addition)
        self.addition.save()
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_completion_sends_email(self):
        self.addition = models.Addition.objects.create(
            owner=self.owner,
            plate='REAL_MEDALLION',
        )
        self.addition = self._fill_most_fields(self.addition)

        self.addition.mvr_authorized = timezone.now()
        self.addition.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_completion_with_MVR_sends_email(self):
        self.addition = models.Addition.objects.create(
            owner=self.owner,
            plate='REAL_MEDALLION',
        )
        self.addition = self._fill_most_fields(self.addition)
        self.addition.address_proof_image = 'filled'
        self.addition.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))
