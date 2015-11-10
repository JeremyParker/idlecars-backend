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


def match_list():
    return {
        'DocsApprovedNoBooking': {
            'argument': 'approved_driver',
            'result': settings.WEBAPP_URL + '/#/cars',
        },
        'BaseLetterApprovedNoCheckout': {
            'argument': 'pending_booking',
            'result': settings.WEBAPP_URL + '/#/account/bookings',
        },
        'FirstDocumentsReminderBooking': {
            'argument': 'pending_booking',
            'result': settings.WEBAPP_URL + '/#/bookings',
        },
        'FirstDocumentsReminderDriver': {
            'argument': 'driver',
            'result': settings.WEBAPP_URL + '/#/bookings',
        },
        'SecondDocumentsReminderBooking': {
            'argument': 'pending_booking',
            'result': settings.WEBAPP_URL + '/#/bookings',
        },
        'SecondDocumentsReminderDriver': {
            'argument': 'driver',
            'result': settings.WEBAPP_URL + '/#/bookings',
        },
        'ThirdDocumentsReminderBooking': {
            'argument': 'pending_booking',
            'result': settings.WEBAPP_URL + '/#/bookings',
        },
        'ThirdDocumentsReminderDriver': {
            'argument': 'driver',
            'result': settings.WEBAPP_URL + '/#/bookings',
        },
        'BookingTimedOut': {
            'argument': 'pending_booking',
            'result': settings.WEBAPP_URL + '/#/cars',
        },
        'AwaitingInsuranceEmail': {
            'argument': 'requested_booking',
            'result': 'pre-approved',
        },
        'InsuranceApproved': {
            'argument': 'requested_booking',
            'result': 'approved',
        },
        'CheckoutReceipt': {
            'argument': 'reserved_booking',
            'result': 'hold of $500 on your credit card',
        },
        'PickupConfirmation': {
            'argument': 'booked_booking',
            'result': 'Success!',
        },
        'BookingCanceled': {
            'argument': 'pending_booking',
            'result': 'canceled',
        },
        'PasswordReset': {
            'argument': 'password_reset',
            'result': 'password',
        },
    }


class SmsNotificationTest(TestCase):
    def setUp(self):
        auth_user = server_factories.AuthUser.create(first_name='Tom', last_name='Cat')

        self.driver = server_factories.Driver.create(auth_user=auth_user)
        self.complete_driver = server_factories.CompletedDriver.create()
        self.payment_method_driver = server_factories.PaymentMethodDriver.create()
        self.approved_driver = server_factories.ApprovedDriver.create()
        self.base_letter_driver = server_factories.BaseLetterDriver.create()

        car = server_factories.BookableCar.create(solo_cost=500)
        self.pending_booking = server_factories.Booking.create(car=car)
        self.reserved_booking = server_factories.ReservedBooking.create(car=car)
        self.requested_booking = server_factories.RequestedBooking.create(car=car)
        self.booked_booking = server_factories.BookedBooking.create(car=car)

        self.password_reset = crm_factories.PasswordReset.create(auth_user=auth_user)

        sms_service.test_reset()

    def test_driver_sms(self):
        for name, obj in inspect.getmembers(driver_notifications):
            if inspect.isclass(obj) and name in match_list().keys():
                campaign_name = 'driver_notifications.' + name
                argument = eval('self.' + match_list()[name]['argument'])
                print campaign_name

                crm_factories.SmsCampaign.create(name=campaign_name)
                notification.send(campaign_name, argument)
                self.assertEqual(len(sms_service.test_get_outbox()), 1)
                self.assertTrue(
                    match_list()[name]['result'] in sms_service.test_get_outbox()[0]['body'],
                )

                sms_service.test_reset()
