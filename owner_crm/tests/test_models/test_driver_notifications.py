# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import inspect
import datetime

from django.utils import timezone
from django.test import TestCase
from django.conf import settings

from owner_crm.services import notification
from owner_crm.models import Campaign, driver_notifications
from owner_crm import factories as crm_factories

from idlecars import factories as idlecars_factories
from server import factories as server_factories
from idlecars import sms_service


class DriverNotificationTest(TestCase):
    def setUp(self):
        auth_user = idlecars_factories.AuthUser.create(first_name='Tom', last_name='Cat')

        self.driver = server_factories.Driver.create(auth_user=auth_user)
        self.complete_driver = server_factories.CompletedDriver.create()
        self.payment_method_driver = server_factories.PaymentMethodDriver.create()
        self.approved_driver = server_factories.ApprovedDriver.create()
        self.base_letter_driver = server_factories.BaseLetterDriver.create()

        car = server_factories.BookableCar.create(solo_cost=500)
        self.pending_booking = server_factories.Booking.create(car=car)
        self.reserved_booking = server_factories.ReservedBooking.create(car=car)
        self.requested_booking = server_factories.RequestedBooking.create(car=car)
        self.accepted_booking = server_factories.AcceptedBooking.create(car=car)
        self.booked_booking = server_factories.BookedBooking.create(car=car)

        self.password_reset = crm_factories.PasswordReset.create(auth_user=auth_user)

        self.settled_payment = server_factories.SettledPayment.create(
            booking=self.booked_booking,
            amount=car.solo_cost,
            invoice_start_time=timezone.now(),
            invoice_end_time=timezone.now() + datetime.timedelta(days=7),
        )

        sms_service.test_reset()

        self.notification_spec = {
            'DocsApprovedNoBooking': {
                'argument': 'approved_driver',
                'sms_result': settings.DRIVER_APP_URL + '/#/listing',
                'email_result': self.approved_driver.full_name(),
            },
            'BaseLetterApprovedNoCheckout': {
                'argument': 'pending_booking',
                'sms_result': settings.DRIVER_APP_URL + '/#/account/bookings',
                'email_result': self.pending_booking.car.display_name(),
            },
            'FirstDocumentsReminderBooking': {
                'argument': 'pending_booking',
                'sms_result': settings.DRIVER_APP_URL + '/#/bookings',
                'email_result': self.pending_booking.car.display_name(),
            },
            'FirstDocumentsReminderDriver': {
                'argument': 'driver',
                'sms_result': settings.DRIVER_APP_URL + '/#/bookings',
                'email_result': 'Submit your documents',
            },
            'SecondDocumentsReminderBooking': {
                'argument': 'pending_booking',
                'sms_result': settings.DRIVER_APP_URL + '/#/bookings',
                'email_result': self.pending_booking.car.display_name(),
            },
            'SecondDocumentsReminderDriver': {
                'argument': 'driver',
                'sms_result': settings.DRIVER_APP_URL + '/#/bookings',
                'email_result': 'Are you ready',
            },
            'ThirdDocumentsReminderBooking': {
                'argument': 'pending_booking',
                'sms_result': settings.DRIVER_APP_URL + '/#/bookings',
                'email_result': 'submit your driver documents',
            },
            'ThirdDocumentsReminderDriver': {
                'argument': 'driver',
                'sms_result': settings.DRIVER_APP_URL + '/#/bookings',
                'email_result': 'Are you ready',
            },
            'BookingTimedOut': {
                'argument': 'pending_booking',
                'sms_result': settings.DRIVER_APP_URL + '/#/listings',
                'email_result': self.pending_booking.car.display_name(),
            },
            'AwaitingInsuranceEmail': {
                'argument': 'requested_booking',
                'sms_result': 'pre-approved',
                'email_result': 'submitted',
            },
            'InsuranceApproved': {
                'argument': 'requested_booking',
                'sms_result': 'approved',
                'email_result': self.requested_booking.car.display_name(),
            },
            'CheckoutReceipt': {
                'argument': 'reserved_booking',
                'sms_result': 'hold of $500 on your credit card',
                'email_result': self.reserved_booking.car.display_name(),
            },
            'PickupConfirmation': {
                'argument': 'settled_payment',
                'sms_result': 'Success!',
                'email_result': 'ready to drive',
            },
            'BookingCanceled': {
                'argument': 'pending_booking',
                'sms_result': 'canceled',
                'email_result': 'canceled',
            },
            'PasswordReset': {
                'argument': 'password_reset',
                'sms_result': 'password',
                'email_result': 'your idlecars password',
            },
            'InvitorReceivedCredit': {
                'argument': 'approved_driver',
                'sms_result': 'referral code',
                'email_result': 'credit',
            },
            'UseYourCredit': {
                'argument': 'approved_driver',
                'sms_result': 'next rental',
                'email_result': 'next rental',
            },
            'SignupCredit': {
                'argument': 'driver',
                'sms_result': 'referral code',
                'email_result': 'Idlecars rental',
            },
            'InsuranceRejected': {
                'argument': 'accepted_booking',
                'email_result': 'insurance',
            },
            'InsuranceFailed': {
                'argument': 'accepted_booking',
                'email_result': 'unable',
            },
            'CarRentedElsewhere': {
                'argument': 'requested_booking',
                'email_result': 'Sorry',
            },
            'PaymentReceipt': {
                'argument': 'settled_payment',
                'email_result': 'Received',
            },
            'SomeoneElseBooked': {
                'argument': 'pending_booking',
                'email_result': 'Someone else',
            },
            'PasswordResetConfirmation': {
                'argument': 'password_reset',
                'email_result': 'password',
            },
        }

    def test_driver_notifications(self):
        from django.core import mail

        for name, obj in inspect.getmembers(driver_notifications):
            if inspect.isclass(obj):
                # make sure we know about this Notification
                self.assertTrue(name in self.notification_spec.keys())

                spec = self.notification_spec[name]
                campaign_name = 'driver_notifications.' + name
                campaign = crm_factories.Campaign.create(name=campaign_name)
                argument = eval('self.' + spec['argument'])

                # check the sms if this notification is supposed to support sms
                if 'sms_result' in spec.keys():
                    campaign.preferred_medium = Campaign.SMS_MEDIUM
                    campaign.save()

                    notification.send(campaign_name, argument)

                    # print sms_service.test_get_outbox()[0]['body'] + ' --------------- ' + campaign_name
                    self.assertEqual(len(sms_service.test_get_outbox()), 1)
                    self.assertTrue(spec['sms_result'] in sms_service.test_get_outbox()[0]['body'])
                    sms_service.test_reset()

                # check the email if this notification is supposed to support email
                if 'email_result' in spec.keys():
                    campaign.preferred_medium = Campaign.EMAIL_MEDIUM
                    campaign.save()

                    notification.send(campaign_name, argument)

                    self.assertEqual(len(mail.outbox), 1)
                    # print mail.outbox[0].subject + ' --------------- ' + campaign_name
                    self.assertTrue(spec['email_result'] in mail.outbox[0].subject)

                    # manually reset outbox
                    mail.outbox = []
