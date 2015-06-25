# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server import serializers, factories

class TestDriverSerializer(TestCase):
    def test_all_docs_uploaded_false(self):
        driver = factories.Driver.create()
        self.assertFalse(serializers.DriverSerializer(driver).data['all_docs_uploaded'])

    def test_all_docs_uploaded_true(self):
        driver = factories.Driver.create(
            driver_license_image='taco.jpg',
            fhv_license_image='taco.jpg',
            address_proof_image='taco.jpg',
            defensive_cert_image='taco.jpg',
        )

        self.assertTrue(serializers.DriverSerializer(driver).data['all_docs_uploaded'])
