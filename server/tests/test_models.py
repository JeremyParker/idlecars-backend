# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from server import models
from idlecars import model_helpers

class TestDriver(TestCase):
    def test_full_name(self):
        driver = models.Driver(
            first_name='Henry',
            last_name='Ford',
        )
        self.assertEqual(driver.full_name(), "Henry Ford")

    def test_stripped_char_field(self):
        field = model_helpers.StrippedCharField()
        self.assertIsNone(field.get_prep_value(None))
        self.assertEqual('Charlie', field.get_prep_value('Charlie  '))
        self.assertEqual('ABCDEF', field.get_prep_value('ABCDEF'))
