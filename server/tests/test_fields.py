# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.exceptions import ValidationError

from server.fields import CarColorField


class TestCarColorField(TestCase):
    def setUp(self):
        self.field = CarColorField()

    def test_color_number_to_value(self):
        data = self.field.to_internal_value('black')
        self.assertEqual(data, 0)

    def test_color_number_to_value_caps(self):
        data = self.field.to_internal_value('GREY')
        self.assertEqual(data, 2)

    def test_bad_color_throws_validation_error(self):
        with self.assertRaises(ValidationError):
            self.field.to_internal_value('puke green')

    def test_value_to_formatted_string(self):
        representation = self.field.to_representation(2)
        self.assertEqual(representation, 'Grey')
