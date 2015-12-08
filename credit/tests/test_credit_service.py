# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase

from credit import credit_service
from idlecars.factories import AuthUser


class CreditCodeServiceTest(TestCase):
    def test_create_create_code(self):
        auth_user = AuthUser.create()
        code = credit_service.create_invite_code(auth_user.customer)
        self.assertTrue(len(code.credit_code) <= 8)

        codes = [code.credit_code]
        for n in range(50):
            code = credit_service.create_invite_code(auth_user.customer)
            self.assertFalse(code.credit_code in codes)
            codes.append(code.credit_code)
