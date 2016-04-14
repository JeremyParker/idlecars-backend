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


class OwnerInvitationTest(TestCase):
    def setUp(self):
        self.owner = factories.Owner.create()
        self.phone_number = self.owner.auth_users.latest('pk').username

    def test_invitation_success(self):
        auth_user = owner_service.invite_legacy_owner(self.phone_number)
        self.assertEqual(auth_user.username, self.phone_number)

        password_reset = PasswordReset.objects.get(auth_user=auth_user)
        self.assertIsNotNone(password_reset)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        email = self.owner.auth_users.first().email
        self.assertEqual(outbox[0].merge_vars.keys()[0], email)
        self.assertEqual(
            outbox[0].merge_vars[email]['CTA_URL'],
            app_routes_owner.password_reset(password_reset),
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))
        self.assertEqual(
            outbox[0].subject,
            'Complete your account today - sign up with your bank account and start getting paid'
        )

    def test_invitation_no_owner(self):
        self.user = AuthUser.create() # Note: no owner
        with self.assertRaises(Owner.DoesNotExist):
            auth_user = owner_service.invite_legacy_owner(self.user.username)

    def test_invitation_no_user(self):
        with self.assertRaises(Owner.DoesNotExist):
            auth_user = owner_service.invite_legacy_owner('0000') # Note - bad phone number


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
