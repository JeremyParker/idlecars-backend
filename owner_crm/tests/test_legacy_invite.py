# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.management import call_command

import server.factories


class TestLegacyInvite(TestCase):
    def setUp(self):
        auth_user = server.factories.AuthUser.create(username='1234567890')
        self.driver = server.factories.Driver.create(auth_user=auth_user)

    def test_legacy_invite(self):
        call_command('legacy_invite', '1234567890')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'An account has been created for you at idlecars'
        )
