# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib.auth import models as auth_models

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

import server.factories
from owner_crm import models
import owner_crm.factories


class PasswordResetTest(APITestCase):
    def setUp(self):
        self.auth_user = server.factories.AuthUser.create(password='old_password')
        self.password_reset = owner_crm.factories.PasswordReset.create(auth_user=self.auth_user)

        # we need a driver so we know if we can SMS them or not.
        self.driver = server.factories.Driver.create(auth_user=self.auth_user)

    def _make_request(self):
        data = {
            'password': 'new_password',
            'token': self.password_reset.token,
        }
        url = reverse('owner_crm:password_resets')
        return APIClient().patch(url, data)

    def test_reset_success(self):
        old_password = self.auth_user.password
        response = self._make_request()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.content)

        self.assertEqual(models.PasswordReset.objects.count(), 1)
        password_reset = models.PasswordReset.objects.first()
        self.assertEqual(password_reset.state, models.ConsumableToken.STATE_CONSUMED)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].subject, 'Your idlecars password has been set. ')

        self.auth_user = auth_models.User.objects.get(id=self.auth_user.id)
        new_password = self.auth_user.password
        self.assertNotEqual(old_password, new_password)
        self.assertTrue(self.auth_user.check_password('new_password'))

    def test_reset_fail_no_token(self):
        data = {'password': 'new_password'}
        url = reverse('owner_crm:password_resets')
        response = APIClient().patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO - put this back in when we consume tokens again
    # def test_reset_fail_token_consumed(self):
    #     self.password_reset.state = models.ConsumableToken.STATE_CONSUMED
    #     self.password_reset.save()
    #     response = self._make_request()
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_token_expired(self):
        # TODO - we should expire the token after a couple of hours
        pass

    def test_reset_bad_token(self):
        data = {
            'password': 'new_password',
            'token': 'wrong_token',
        }
        url = reverse('owner_crm:password_resets')
        response = APIClient().patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_invalidates_old_auth_token(self):
        old_token = Token.objects.get(user__username=self.auth_user.username)

        response = self._make_request()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_token = Token.objects.get(user__username=self.auth_user.username)
        self.assertNotEqual(old_token, new_token)
