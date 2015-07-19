# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

import server.factories
from owner_crm import models
import owner_crm.factories


class PasswordResetTest(APITestCase):
    def setUp(self):
        self.auth_user = server.factories.AuthUser.create()
        self.password_reset = owner_crm.factories.PasswordReset.create(auth_user=self.auth_user)

    def _make_request(self):
        data = {
            'password': 'somepassword',
            'token': self.password_reset.token,
        }
        url = reverse('owner_crm:password_resets')
        return APIClient().patch(url, data)

    def test_reset_success(self):
        response = self._make_request()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(models.PasswordReset.objects.count(), 1)
        password_reset = models.PasswordReset.objects.first()
        self.assertEqual(password_reset.state, models.ConsumableToken.STATE_CONSUMED)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_reset_fail_no_token(self):
        data = {'password': 'somepass'}
        url = reverse('owner_crm:password_resets')
        response = APIClient().patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_fail_token_consumed(self):
        self.password_reset.state = models.ConsumableToken.STATE_CONSUMED
        self.password_reset.save()
        response = self._make_request()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_token_expired(self):
        # TODO - we should expire the token after a couple of hours
        pass

    def test_reset_bad_token(self):
        data = {
            'password': 'somepassword',
            'token': 'wrong_token',
        }
        url = reverse('owner_crm:password_resets')
        response = APIClient().patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
