# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from owner_crm.models import Campaign
from owner_crm.services import message_service

from server import factories


class MessageServiceTest(TestCase):
    def setUp(self):
        self.driver = factories.BaseLetterDriver.create()
        self.campaign_name = 'driver_messages.docs_approved_no_booking'

    def test_message_create_campaign(self):
        self.assertEqual(len(Campaign.objects.all()), 0)

        message_service.send(self.campaign_name, self.driver, self.driver)
        self.assertEqual(len(Campaign.objects.all()), 1)

    def test_message_campaign_already_exists(self):
        Campaign.objects.create(name=self.campaign_name)
        self.assertEqual(len(Campaign.objects.all()), 1)

        # make sure this do not create another campaign
        message_service.send(self.campaign_name, self.driver, self.driver)
        self.assertEqual(len(Campaign.objects.all()), 1)




