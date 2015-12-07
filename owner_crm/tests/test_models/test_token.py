# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from owner_crm import factories

class TestToken(TestCase):
    def test_token_is_unique(self):
        first_reset = factories.PasswordReset.create()
        other_reset = factories.PasswordReset.create()

        self.assertNotEqual(first_reset.token.strip(), '')
        self.assertNotEqual(other_reset.token.strip(), '')

        self.assertNotEqual(first_reset, other_reset)
