# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import inspect
import datetime

from django.utils import timezone
from django.test import TestCase

from owner_crm.services import notification
from owner_crm.models import Campaign, owner_notifications
from owner_crm import factories as crm_factories

from server import factories as server_factories
from idlecars import sms_service, client_side_routes


class OwnerNotificationTest(TestCase):
    def setUp(self):
        auth_user = server_factories.AuthUser.create(first_name='Tom', last_name='Cat')

        self.bank_account_owner = server_factories.BankAccountOwner.create()

        car = server_factories.BookableCar.create(solo_cost=500)
        self.requested_booking = server_factories.RequestedBooking.create(car=car)
        self.booked_booking = server_factories.BookedBooking.create(car=car)

        self.renewal = crm_factories.Renewal.create(car=car)
        self.password_reset = crm_factories.PasswordReset.create(auth_user=auth_user)

        self.settled_payment = server_factories.SettledPayment.create(
            booking=self.booked_booking,
            amount=car.solo_cost,
            invoice_start_time=timezone.now(),
            invoice_end_time=timezone.now() + datetime.timedelta(days=7),
        )

        sms_service.test_reset()

        self.notification_spec = {
            'RenewalEmail': {
                'argument': 'renewal',
                'sms_result': client_side_routes.renewal_url(self.renewal),
                'email_result': 'expire',
            },
            'NewBookingEmail': {
                'argument': 'requested_booking',
                'email_result': self.requested_booking.car.display_name(),
            },
            'FirstMorningInsuranceReminder': {
                'argument': 'requested_booking',
                'email_result': self.requested_booking.car.display_name(),
                'sms_result': self.requested_booking.driver.full_name(),
            },
            'SecondMorningInsuranceReminder': {
                'argument': 'requested_booking',
                'email_result': self.requested_booking.car.display_name(),
                'sms_result': self.requested_booking.driver.full_name(),
            },
            'FirstAfternoonInsuranceReminder': {
                'argument': 'requested_booking',
                'email_result': self.requested_booking.car.display_name(),
                'sms_result': self.requested_booking.driver.full_name(),
            },
            'SecondAfternoonInsuranceReminder': {
                'argument': 'requested_booking',
                'email_result': self.requested_booking.car.display_name(),
                'sms_result': self.requested_booking.driver.full_name(),
            },
            'PickupConfirmation': {
                'argument': 'booked_booking',
                'email_result': 'paid',
                'sms_result': self.booked_booking.driver.full_name()
            },
            'PaymentReceipt': {
                'argument': 'settled_payment',
                'email_result': 'receipt',
            },
            'BookingCanceled': {
                'argument': 'requested_booking',
                'email_result': 'canceled',
                'sms_result': self.requested_booking.driver.first_name(),
            },
            'DriverRejected': {
                'argument': 'requested_booking',
                'email_result': 'canceled',
                'sms_body': self.requested_booking.driver.first_name(),
            },
            'InsuranceTooSlow': {
                'argument': 'requested_booking',
                'email_result': 'canceled',
            },
            'AccountCreated': {
                'argument': 'password_reset',
                'email_result': 'account',
            },
            'BankAccountApproved': {
                'argument': 'bank_account_owner',
                'email_result': 'approved',
            },
            'PasswordReset': {
                'argument': 'password_reset',
                'email_result': 'Reset your password',
                'sms_result': self.password_reset.token,
            },
        }

    def test_owner_notifications(self):
        from django.core import mail

        for name, obj in inspect.getmembers(owner_notifications):
            if inspect.isclass(obj):
                # make sure we know about this Notification
                self.assertTrue(name in self.notification_spec.keys())

                spec = self.notification_spec[name]
                campaign_name = 'owner_notifications.' + name
                campaign = crm_factories.Campaign.create(name=campaign_name)
                argument = eval('self.' + spec['argument'])

                # check the sms if this notification is supposed to support sms
                if 'sms_result' in spec.keys():
                    campaign.preferred_medium = Campaign.SMS_MEDIUM
                    campaign.save()

                    # print 'sms: ' + campaign_name
                    notification.send(campaign_name, argument)

                    self.assertEqual(len(sms_service.test_get_outbox()), 1)
                    self.assertTrue(spec['sms_result'] in sms_service.test_get_outbox()[0]['body'])
                    sms_service.test_reset()

                # check the email if this notification is supposed to support email
                if 'email_result' in spec.keys():
                    campaign.preferred_medium = Campaign.EMAIL_MEDIUM
                    campaign.save()

                    notification.send(campaign_name, argument)

                    self.assertEqual(len(mail.outbox), 1)
                    # print mail.outbox[0].subject + ' --------------- Email: ' + campaign_name
                    self.assertTrue(spec['email_result'] in mail.outbox[0].subject)

                    # manually reset outbox
                    mail.outbox = []
