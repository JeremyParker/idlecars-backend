# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from idlecars import sms_service
from server import factories

from owner_crm.models import Campaign, Message
from owner_crm.services import notification as notification_service


def verify_throttled_on_booking(booking, campaign):
    throttle_messages = Message.objects.filter(booking=booking, campaign=campaign)
    assert(len(throttle_messages) == 1)


def verify_throttled_on_driver(driver, campaign):
    throttle_messages = Message.objects.filter(driver=driver, campaign=campaign)
    assert(len(throttle_messages) == 1)


def verify_throttled_on_owner(owner, campaign):
    throttle_messages = Message.objects.filter(owner=owner, campaign=campaign)
    assert(len(throttle_messages) == 1)


class NotificationServiceTest(TestCase):
    def setUp(self):
        sms_service.test_reset() # need to reset the sms outbox between every test
        self.driver = factories.BaseLetterDriver.create()
        self.campaign_name = 'driver_notifications.DocsApprovedNoBooking'

    def test_notification_create_campaign(self):
        self.assertEqual(len(Campaign.objects.all()), 0)

        notification_service.send(self.campaign_name, self.driver)
        self.assertEqual(len(Campaign.objects.all()), 1)

    def test_notification_campaign_already_exists(self):
        Campaign.objects.create(name=self.campaign_name)
        self.assertEqual(len(Campaign.objects.all()), 1)

        # make sure this do not create another campaign
        notification_service.send(self.campaign_name, self.driver)
        self.assertEqual(len(Campaign.objects.all()), 1)

    def test_existing_campaign_with_sms(self):
        Campaign.objects.create(name=self.campaign_name, preferred_medium=Campaign.SMS_MEDIUM)
        self.assertEqual(len(Campaign.objects.all()), 1)

        notification_service.send(self.campaign_name, self.driver)

        # we should have sent one SMS
        outbox = sms_service.test_get_outbox()
        self.assertEqual(len(outbox), 1)
        sms = outbox[0]
        self.assertEqual(sms['to'], '+1{}'.format(self.driver.phone_number()))
        self.assertIsNotNone(sms['body'])
