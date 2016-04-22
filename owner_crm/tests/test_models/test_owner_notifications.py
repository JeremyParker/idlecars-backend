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
from server.models import OnboardingOwner
from idlecars import factories as idlecars_factories
from idlecars import sms_service, app_routes_owner


class OwnerNotificationTest(TestCase):
    def setUp(self):
        auth_user = idlecars_factories.AuthUser.create(first_name='Tom', last_name='Cat')

        self.onboarding_owner = OnboardingOwner.objects.create(
            phone_number='1234567890',
            name='onboarding_owner',
        )
        self.owner = server_factories.Owner.create()
        self.bank_account_owner = server_factories.Owner.create()

        self.car = server_factories.BookableCar.create(weekly_rent=500)
        self.pending_booking = server_factories.Booking.create()
        self.requested_booking = server_factories.RequestedBooking.create(car=self.car)
        self.returned_booking = server_factories.ReturnedBooking.create(car=self.car)

        self.password_reset = crm_factories.PasswordReset.create(
            auth_user=self.bank_account_owner.auth_users.first()
        )

        sms_service.test_reset()

        self.notification_spec = {
            'RenewalEmail': {
                'argument': 'car',
                'sms_result': app_routes_owner.car_details_url(self.car),
                'email_result': 'expire',
            },
            'SignupConfirmation': {
                'argument': 'owner',
                'sms_body': 'Welcome',
                'email_result': 'Welcome',
            },
            'FirstAccountReminder': {
                'argument': 'owner',
                'sms_body': 'incomplete',
                'email_result': 'incomplete',
            },
            'SecondAccountReminder': {
                'argument': 'owner',
                'sms_body': 'complete',
                'email_result': 'Complete',
            },
            'NewBookingEmail': {
                'argument': 'requested_booking',
                'email_result': self.requested_booking.car.display_name(),
                'sms_result': self.requested_booking.car.owner.auth_users.first().email,
            },
            # 'FirstMorningInsuranceReminder': {
            #     'argument': 'requested_booking',
            #     'email_result': self.requested_booking.car.display_name(),
            #     'sms_result': self.requested_booking.driver.full_name(),
            # },
            # 'SecondMorningInsuranceReminder': {
            #     'argument': 'requested_booking',
            #     'email_result': self.requested_booking.car.display_name(),
            #     'sms_result': self.requested_booking.driver.full_name(),
            # },
            # 'ThirdMorningInsuranceReminder': {
            #     'argument': 'requested_booking',
            #     'email_result': self.requested_booking.driver.full_name(),
            #     'sms_result': self.requested_booking.car.display_name(),
            # },
            # 'FirstAfternoonInsuranceReminder': {
            #     'argument': 'requested_booking',
            #     'email_result': self.requested_booking.car.display_name(),
            #     'sms_result': self.requested_booking.driver.full_name(),
            # },
            # 'SecondAfternoonInsuranceReminder': {
            #     'argument': 'requested_booking',
            #     'email_result': self.requested_booking.car.display_name(),
            #     'sms_result': self.requested_booking.driver.full_name(),
            # },
            # 'ThirdAfternoonInsuranceReminder': {
            #     'argument': 'requested_booking',
            #     'email_result': self.requested_booking.driver.full_name(),
            #     'sms_result': self.requested_booking.car.display_name(),
            # },
            'PendingNotification': {
                'argument': 'pending_booking',
                'email_result': 'interested',
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
            'BankAccountApproved': {
                'argument': 'bank_account_owner',
                'email_result': 'approved',
            },
            'PasswordReset': {
                'argument': 'password_reset',
                'email_result': 'Reset your All Taxi password',
                'sms_result': self.password_reset.token,
            },
            'PasswordResetConfirmation': {
                'argument': 'password_reset',
                'email_result': 'password',
                'sms_result': 'password',
            },
        }

    def test_owner_notifications(self):
        from django.core import mail

        for name, obj in inspect.getmembers(owner_notifications):
            if inspect.isclass(obj):
                # make sure we know about this Notification
                if not name in self.notification_spec.keys():
                    continue
                self.assertTrue(name in self.notification_spec.keys())

                spec = self.notification_spec[name]
                campaign_name = 'owner_notifications.' + name
                campaign = crm_factories.Campaign.create(name=campaign_name)
                argument = eval('self.' + spec['argument'])

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
