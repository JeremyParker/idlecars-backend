# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import inspect

from django.test import TestCase
from django.conf import settings

from owner_crm.services import notification
from owner_crm.models import Campaign, driver_notifications
from owner_crm import factories as crm_factories

from server import factories as server_factories
from idlecars import sms_service


def argument_list():
    return {
        'DocsApprovedNoBooking': 'approved_driver',
        'BaseLetterApprovedNoCheckout': 'pending_booking',
    }

def result_list():
    return {
        'DocsApprovedNoBooking': settings.WEBAPP_URL + '/#/cars',
        'BaseLetterApprovedNoCheckout': settings.WEBAPP_URL + '/#/account/bookings',
    }

class SmsNotificationTest(TestCase):
    def setUp(self):
        self.driver = server_factories.Driver.create()
        self.complete_driver = server_factories.CompletedDriver.create()
        self.payment_method_driver = server_factories.PaymentMethodDriver.create()
        self.approved_driver = server_factories.ApprovedDriver.create()
        self.base_letter_driver = server_factories.BaseLetterDriver.create()

        self.pending_booking = server_factories.Booking.create()
        self.reserved_booking = server_factories.ReservedBooking.create()


        sms_service.test_reset()

    def test_driver_sms(self):
        for name, obj in inspect.getmembers(driver_notifications):
            if inspect.isclass(obj) and name in argument_list().keys():
                campaign_name = 'driver_notifications.' + name
                argument = eval('self.' + argument_list()[name])
                print argument

                crm_factories.SmsCampaign.create(name=campaign_name)
                notification.send(campaign_name, argument)
                self.assertEqual(len(sms_service.test_get_outbox()), 1)
                self.assertTrue(
                    result_list()[name] in sms_service.test_get_outbox()[0]['body'],
                )

                sms_service.test_reset()
