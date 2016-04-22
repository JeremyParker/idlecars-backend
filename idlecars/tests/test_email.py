# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from idlecars import email


class EmailTest(TestCase):
    '''
    Unit tests for email service. Just testing the stuff in email.py.
    '''
    def test_send(self):
        merge_vars = {
            'jeremy@alltaxiny.com': {
                'FNAME': 'Robert',
                'TEXT': 'have lunch with me',
                'CTA_LABEL': 'Press a button',
                'CTA_URL': 'http://idlecars.com',
                'HEADLINE': 'Welcome to the End Of The World!',
            },
        }

        result = email.send_async(
            template_name='one_button_no_image',
            subject='Tested!',
            merge_vars=merge_vars,
        )

        # Test that one message has been sent
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        # make sure all the values made it to the sent message
        self.assertEqual(outbox[0].subject, 'Tested!')
        self.assertEqual(outbox[0].merge_vars, merge_vars)
        self.assertEqual(outbox[0].template_name, 'one_button_no_image')

    def test_multiple_recipients(self):
        merge_vars = {
            'jeff@alltaxiny.com': {'FNAME': "McFly"},
            'jeremy@alltaxiny.com': {'FNAME': "Jeremy"},
        }

        result = email.send_async(
            template_name='one_button_no_image',
            subject='Tested!',
            merge_vars=merge_vars,
        )

        from django.core.mail import outbox
        self.assertEqual(len(outbox[0].recipients()), 2)
        self.assertEqual(outbox[0].merge_vars, merge_vars)
