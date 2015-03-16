# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
import models

class TestDriver(TestCase):
	def test_full_name(self):
		driver = models.Driver(
			first_name='Henry',
			last_name='Ford',
		)
		self.assertEqual(driver.full_name(), "Henry Ford")
