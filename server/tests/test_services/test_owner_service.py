# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

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
            client_side_routes.owner_password_reset(password_reset),
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_invitation_no_owner(self):
        self.user = factories.AuthUser.create() # Note: no owner
        with self.assertRaises(Owner.DoesNotExist):
            auth_user = owner_service.invite_legacy_owner(self.user.username)

    def test_invitation_no_user(self):
        with self.assertRaises(Owner.DoesNotExist):
            auth_user = owner_service.invite_legacy_owner('0000') # Note - bad phone number
