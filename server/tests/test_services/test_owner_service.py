# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase

from idlecars import client_side_routes
from owner_crm.tests import sample_merge_vars
from owner_crm.models import PasswordReset


from server import factories
from server.services import owner_service
from server.models import Owner


class OwnerInvitationTest(TestCase):
    def setUp(self):
        self.owner = factories.Owner.create()
        self.user_account = factories.UserAccount.create(owner=self.owner)

    def test_invitation_success(self):
        created, auth_user = owner_service.invite_legacy_owner(self.user_account.phone_number)
        self.assertEqual(auth_user.username, self.user_account.phone_number)
        self.assertTrue(created)

        password_reset = PasswordReset.objects.get(auth_user=auth_user)
        self.assertIsNotNone(password_reset)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].merge_vars.keys()[0], self.user_account.email)
        self.assertEqual(
            outbox[0].merge_vars[self.user_account.email]['CTA_URL'],
            client_side_routes.owner_password_reset(password_reset),
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_invitation_no_owner(self):
        self.user_account = factories.UserAccount.create() # Note - no owner
        with self.assertRaises(Owner.DoesNotExist):
            created, auth_user = owner_service.invite_legacy_owner(self.user_account.phone_number)

    def test_invitation_no_user_account(self):
        with self.assertRaises(Owner.DoesNotExist):
            created, auth_user = owner_service.invite_legacy_owner('0000') # Note - bad phone number

    def test_invitation_existing_auth_user(self):
        auth_user = factories.AuthUser.create(username=self.user_account.phone_number)
        self.owner.auth_users.add(auth_user)

        created, new_auth_user = owner_service.invite_legacy_owner(self.user_account.phone_number)
        self.assertEqual(len(self.owner.auth_users.all()), 1)
        self.assertEqual(new_auth_user, auth_user)
