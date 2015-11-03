# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.conf import settings

from idlecars import sms_service


class SmsTest(TestCase):
    '''
    Unit tests for sms_service. Really, it's just testing the FakeSmsClient.
    '''
    def setUp(self):
        sms_service.test_reset()

    def test_send_sync(self):
        result = sms_service.send_sync(to='+16176428092', body='hi')
        self.assertIsNone(result.error_message)
        self.assertEqual(sms_service.test_get_outbox()[0]['body'], 'hi')

    def test_send_async(self):
        sms_service.send_async(to='+16176428092', body='sent asychronously!')
        self.assertEqual(sms_service.test_get_outbox()[0]['body'], 'sent asychronously!')
