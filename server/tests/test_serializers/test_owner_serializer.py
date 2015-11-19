# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server import serializers, factories


class TestOwnerSerializer(TestCase):
    def test_bank_account_null(self):
        owner = factories.Owner.create()
        serializer = serializers.OwnerSerializer(owner).data
        self.assertEqual(serializer['bank_account_state'], 'Add now')

    def test_bank_account_pending(self):
        owner = factories.PendingOwner.create()
        serializer = serializers.OwnerSerializer(owner).data
        self.assertEqual(serializer['bank_account_state'], 'Pending')

    def test_bank_account_approved(self):
        owner = factories.BankAccountOwner.create()
        serializer = serializers.OwnerSerializer(owner).data
        self.assertEqual(serializer['bank_account_state'], 'Approved')

    def test_bank_account_declined(self):
        owner = factories.DeclinedOwner.create()
        serializer = serializers.OwnerSerializer(owner).data
        self.assertEqual(serializer['bank_account_state'], 'Declined')
