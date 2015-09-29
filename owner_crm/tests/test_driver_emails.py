# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server import factories
from owner_crm.services import driver_emails


class TestDriverEmails(TestCase):

    def test_documents_reminder_with_no_missing_docs(self):
        '''
        make sure reminders email is robust enough that it doesn't crash
        if there's driver will all docs uploaded for some reason
        '''
        driver = factories.CompletedDriver.create()
        driver_emails.documents_reminder(driver)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)
