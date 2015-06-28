# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from crm import factories

class TestRenewal(TestCase):
    def test_token_is_unique(self):
        first_renewal = factories.Renewal.create()
        other_renewal = factories.Renewal.create()

        self.assertNotEqual(first_renewal.token.strip(), '')
        self.assertNotEqual(other_renewal.token.strip(), '')

        self.assertNotEqual(first_renewal, other_renewal)
