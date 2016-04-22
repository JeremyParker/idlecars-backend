# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from idlecars import app_routes_owner
from idlecars.factories import AuthUser
from owner_crm.tests import sample_merge_vars
from owner_crm.models import PasswordReset

from server import factories
from server.services import owner_service
from server.models import Owner


class OwnerServiceTest(TestCase):
    def setUp(self):
        self.owner = factories.Owner.create()

    def test_owner_signup(self):
        owner_service.on_set_email(self.owner)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'Welcome to your All Taxi owner account',
        )


class OwnerAccountTest(TestCase):
    def setUp(self):
        self.owner = factories.Owner.create()

    def test_owner_account_declined(self):
        owner_service.update_account_state(
            self.owner.merchant_id,
            Owner.BANK_ACCOUNT_DECLINED,
            ['test fake errors'],
        )

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            '{}\'s bank account was declined'.format(self.owner.name())
        )
