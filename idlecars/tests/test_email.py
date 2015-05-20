# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from idlecars import email


from django.core.mail import EmailMessage, outbox


class EmailTest(TestCase):
    def test_send(self):
        merge_vars = {
            'jeremy@idlecars.com': {'FNAME': "Jeremy"},
        }

        result = email.MandrillEmail().send_async(
            template_name='single_cta',
            subject='Tested!',
            merge_vars=merge_vars,
        )

        # Test that one message has been sent
        self.assertEqual(result, 1)
