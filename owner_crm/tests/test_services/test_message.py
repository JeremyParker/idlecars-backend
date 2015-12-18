# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase
from django.utils import timezone

from idlecars import sms_service
from server import factories as server_factories

from owner_crm.models import Campaign, Message
from owner_crm.services import notification as notification_service
from owner_crm import factories as crm_factories


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
        self.driver = server_factories.BaseLetterDriver.create()
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

    def test_send_sms_with_no_sms_context_sends_email(self):
        car = server_factories.BookableCar.create(weekly_rent=500)
        self.booked_booking = server_factories.BookedBooking.create(car=car)
        self.settled_payment = server_factories.SettledPayment.create(
            booking=self.booked_booking,
            amount=car.weekly_rent,
            invoice_start_time=timezone.now(),
            invoice_end_time=timezone.now() + datetime.timedelta(days=7),
        )

        campaign_name = 'driver_notifications.PaymentReceipt'
        campaign = crm_factories.SmsCampaign.create(name=campaign_name)
        notification_service.send(campaign_name, self.settled_payment)

        self.assertEqual(len(sms_service.test_get_outbox()), 0) # we didn't send an SMS

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_send_both_sends_both(self):
        driver = server_factories.Driver.create()
        campaign_name = 'driver_notifications.FirstDocumentsReminderDriver'
        campaign = crm_factories.SmsCampaign.create(
            name=campaign_name,
            preferred_medium=Campaign.BOTH_MEDIUM,
        )
        notification_service.send(campaign_name, driver)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        self.assertEqual(len(sms_service.test_get_outbox()), 1)
