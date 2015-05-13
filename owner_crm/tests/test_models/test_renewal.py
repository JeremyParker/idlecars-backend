# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from owner_crm import factories

class TestRenewal(TestCase):
    def test_token_is_unique(self):
        first_renewal = factories.Renewal.create()
        other_renewal = factories.Renewal.create()

        first_token = first_renewal.token.strip()
        other_token = other_renewal.token.strip()

        self.assertNotEqual(first_token, '')
        self.assertNotEqual(other_token, '')

        self.assertNotEqual(first_token, other_token)
