# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.conf import settings


class SettingsTest(TestCase):

    def test_heap_app_id(self):
        self.assertEquals(settings.HEAP_APP_ID, '655181858', 'Tests are NOT using the local Heap app id.')
