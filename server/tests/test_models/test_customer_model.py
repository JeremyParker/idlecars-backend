# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server.services import credit_code
from server import factories


class CreditCodeModelTest(TestCase):
    def test_new_driver_has_customer(self):
        driver = factories.ApprovedDriver.create()
        self.assertTrue(driver.auth_user.customer)
