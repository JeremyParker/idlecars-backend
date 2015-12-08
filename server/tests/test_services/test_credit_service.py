# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server import factories


class CreditCodeBackfillTest(TestCase):
    def test_credit_code_backfill(self):
        d1 = factories.Driver.create()
        d2 = factories.ApprovedDriver.create()

        from server.backfills import _20151207_credit_codes
        _20151207_credit_codes.run_backfill_credit_codes()

        d1.auth_user.customer.refresh_from_db()
        self.assertFalse(d1.auth_user.customer.invite_code)

        d2.auth_user.customer.refresh_from_db()
        self.assertTrue(d2.auth_user.customer.invite_code)
