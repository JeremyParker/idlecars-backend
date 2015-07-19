# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

import server.factories
from owner_crm import models
import owner_crm.factories


class PasswordResetExecutionTest(APITestCase):
    def setUp(self):
        auth_user = server.factories.AuthUser.create()
        # self.driver = server_factories.Driver.create(auth_user=user)
        password_reset = owner_crm.factories.PasswordReset.create(auth_user=user)

    # def test_execution_success(self):
    #     data = {'phone_number': self.auth_user.username}
    #     url = reverse('owner_crm:password_executions')
    #     response = APIClient().post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     self.assertEqual(models.PasswordReset.objects.count(), 1)
    #     self.assertEqual(models.PasswordReset.objects.first().auth_user, self.driver.auth_user)

    #     from django.core.mail import outbox
    #     self.assertEqual(len(outbox), 1)
