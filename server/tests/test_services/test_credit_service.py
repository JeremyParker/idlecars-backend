# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server.services import credit_code as credit_code_service
from server import factories


class CreditCodeServiceTest(TestCase):
    def test_create_create_code(self):
        driver = factories.ApprovedDriver.create()
        code = credit_code_service.create_invite_code(driver.auth_user.customer)
        self.assertTrue(len(code.credit_code) <= 8)

        codes = [code.credit_code]
        for n in range(50):
            code = credit_code_service.create_invite_code(driver.auth_user.customer)
            self.assertFalse(code.credit_code in codes)
            codes.append(code.credit_code)

    def test_credit_code_backfill(self):
        d1 = factories.Driver.create()
        d2 = factories.ApprovedDriver.create()

        from server.backfills import _20151207_credit_codes
        _20151207_credit_codes.run_backfill_credit_codes()

        d1.auth_user.customer.refresh_from_db()
        self.assertFalse(d1.auth_user.customer.invite_code)

        d2.auth_user.customer.refresh_from_db()
        self.assertTrue(d2.auth_user.customer.invite_code)
