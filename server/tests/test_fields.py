# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.exceptions import ValidationError

from idlecars import model_helpers
from server import fields

class TestPhoneNumberField(TestCase):
    def test_good_number_to_value(self):
        phone_number = fields.PhoneNumberField()
        data = phone_number.to_internal_value('1234567890')
        self.assertEqual(data, '1234567890')

    def test_bad_number_throws_validation_error(self):
        phone_number = fields.PhoneNumberField()
        with self.assertRaises(ValidationError):
            phone_number.to_internal_value('123')

    def test_value_to_formatted_string(self):
        phone_number = fields.PhoneNumberField()
        representation = phone_number.to_representation('1234567890')
        self.assertEqual(representation, '(123) 456-7890')

