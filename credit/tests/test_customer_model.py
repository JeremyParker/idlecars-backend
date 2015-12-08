# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase


class CreditCodeModelTest(TestCase):
    def test_new_driver_has_customer(self):
        User = get_user_model()
        u = User.objects.create()
        self.assertTrue(u.customer)
