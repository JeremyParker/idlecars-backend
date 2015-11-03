# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.conf import settings

from idlecars import sms_service


class SmsTest(TestCase):
    '''
    Unit tests for sms_service.
    '''
    def test_get_client(self):
        client = sms_service._get_client()
        self.assertIsNotNone(client)

    def test_client_is_singleton(self):
        client1 = sms_service._get_client()
        client2 = sms_service._get_client()
        self.assertTrue(client1 is client2)

    def test_send_sync(self):
        result = sms_service.send_sync(to='+16176428092', body='hi')
        self.assertIsNone(result.error_message)

    def test_send_async(self):
        sms_service.send_async(to='+16176428092', body='sent asychronously!')
