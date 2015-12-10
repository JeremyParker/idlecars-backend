# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from credit import credit_service
from idlecars.factories import AuthUser


class CreditCodeServiceTest(TestCase):
    def test_create_create_code_no_customer(self):
        code = credit_service.create_invite_code('20.00')
        # code string should be between 4 and 8 characters
        self.assertTrue(len(code.credit_code) <= 8)
        self.assertTrue(len(code.credit_code) >= 4)

        self.assertEqual(code.credit_amount, decimal.Decimal('20.00'))
        self.assertEqual(code.invitor_credit_amount, decimal.Decimal('0.00'))
        self.assertEqual(code.redeem_count, 0)

    def test_codes_are_unique(self):
        codes = []
        for n in range(200):
            code = credit_service.create_invite_code('0.0')
            self.assertFalse(code.credit_code in codes)
            codes.append(code.credit_code)

    def test_create_create_code_with_customer(self):
        auth_user = AuthUser.create()
        code = credit_service.create_invite_code(
            '50.00',
            '50.00',
            auth_user.customer
        )
        self.assertEqual(auth_user.customer.invite_code, code)

        self.assertTrue(len(code.credit_code) <= 8)
        self.assertTrue(len(code.credit_code) >= 4)

        self.assertEqual(code.credit_amount, decimal.Decimal('50.00'))
        self.assertEqual(code.invitor_credit_amount, decimal.Decimal('50.00'))
        self.assertEqual(code.redeem_count, 0)

    def test_codes_with_customer_are_unique(self):
        auth_user = AuthUser.create()
        codes = []
        for n in range(200):
            code = credit_service.create_invite_code('0.0', '0.0', auth_user.customer)
            self.assertFalse(code.credit_code in codes)
            codes.append(code.credit_code)

    def test_redeem_code_success(self):
        existing_user = AuthUser.create()
        code = credit_service.create_invite_code(
            '50.00',
            '50.00',
            existing_user.customer
        )

        # new user comes along and redeems the code
        new_user = AuthUser.create()
        credit_service.redeem_code(code.credit_code, new_user.customer)

        # I should have got my sign-up credit!
        self.assertEqual(new_user.customer.app_credit, decimal.Decimal('50.00'))

        # redeem count should go up by 1
        code.refresh_from_db()
        self.assertEqual(code.redeem_count, 1)

    def test_on_cash_spent(self):
        existing_user = AuthUser.create()
        code = credit_service.create_invite_code(
            '50.00',
            '50.00',
            existing_user.customer,
        )

        # new user comes along, redeems code and spends some cash
        new_user = AuthUser.create()
        credit_service.redeem_code(code.credit_code, new_user.customer)
        credit_service.on_cash_spent(new_user.customer)

        # The invitor should have got some app credit
        existing_user.customer.refresh_from_db()
        self.assertEqual(existing_user.customer.app_credit, code.invitor_credit_amount)
