# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

import server.factories
import owner_crm.factories
from owner_crm import models


class PasswordResetSetupTest(APITestCase):
    def setUp(self):
        self.driver = server.factories.Driver.create()

    def test_setup_success_driver(self):
        # look ma! No password reset tokens!
        self.assertEqual(models.PasswordReset.objects.count(), 0)

        data = {'phone_number': self.driver.phone_number()}
        url = reverse('owner_crm:password_reset_setups')
        response = APIClient().post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(models.PasswordReset.objects.count(), 1)
        self.assertEqual(models.PasswordReset.objects.first().auth_user, self.driver.auth_user)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].subject, 'Reset your password on idlecars.')

    def test_setup_success_owner(self):
        # look ma! No password reset tokens!
        self.assertEqual(models.PasswordReset.objects.count(), 0)

        owner = server.factories.Owner.create()
        data = {'phone_number': owner.phone_number()}
        url = reverse('owner_crm:password_reset_setups')
        response = APIClient().post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(models.PasswordReset.objects.count(), 1)
        self.assertEqual(models.PasswordReset.objects.first().auth_user, owner.auth_users.first())

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].subject, 'Reset your password on idlecars.')

    def test_revokes_other_tokens(self):
        auth_user = server.factories.AuthUser.create()
        driver = server.factories.Driver.create(auth_user=auth_user)
        reset = owner_crm.factories.PasswordReset.create(auth_user=auth_user)
        data = {'phone_number': auth_user.username}
        url = reverse('owner_crm:password_reset_setups')
        response = APIClient().post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(models.PasswordReset.objects.count(), 2)

        # check that our original password reset object was revoked.
        reset = models.PasswordReset.objects.get(pk=reset.pk)
        self.assertEqual(reset.state, models.ConsumableToken.STATE_RETRACTED)


    def test_success_with_busy_phone_number(self):
        p = self.driver.phone_number()
        # note: this is different from formatting in our PhoneNumberField
        busy_number = "({}).{}.{}".format(p[:3], p[3:6], p[6:])
        data = {'phone_number': busy_number}
        url = reverse('owner_crm:password_reset_setups')
        response = APIClient().post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_setup_bad_phone_data(self):
        data = {'phone_number': '12345'}
        url = reverse('owner_crm:password_reset_setups')
        response = APIClient().post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_setup_wrong_number(self):
        data = {'phone_number': '666-666-6666'}
        url = reverse('owner_crm:password_reset_setups')
        response = APIClient().post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_setup_wrong_number(self):
        data = {'phone_number': '666-666-6666'}
        url = reverse('owner_crm:password_reset_setups')
        response = APIClient().post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

