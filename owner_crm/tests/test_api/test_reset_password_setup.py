# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

import server.factories
from owner_crm import models


class PasswordResetSetupTest(APITestCase):
    def setUp(self):
        user = server.factories.AuthUser.create()
        self.driver = server.factories.Driver.create(auth_user=user)

    def test_setup_success(self):
        # look ma! No password reset tokens!
        self.assertEqual(models.PasswordReset.objects.count(), 0)

        data = {'phone_number': self.driver.phone_number()}
        url = reverse('owner_crm:password_setups')
        response = APIClient().post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(models.PasswordReset.objects.count(), 1)
        self.assertEqual(models.PasswordReset.objects.first().auth_user, self.driver.auth_user)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_setup_bad_phone_data(self):
        data = {'phone_number': '12345'}
        url = reverse('owner_crm:password_setups')
        response = APIClient().post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_setup_wrong_number(self):
        data = {'phone_number': '666-666-6666'}
        url = reverse('owner_crm:password_setups')
        response = APIClient().post(url, data)
        import pdb; pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_setup_wrong_number(self):
        data = {'phone_number': '666-666-6666'}
        url = reverse('owner_crm:password_setups')
        response = APIClient().post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

