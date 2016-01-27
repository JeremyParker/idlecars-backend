# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from freezegun import freeze_time


from django.utils import timezone
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth.models import User

import idlecars.app_routes_driver
import server.models
import server.factories
from server.services import owner_service
from server.services import booking as booking_service

import owner_crm.models
import owner_crm.factories
from owner_crm.management.commands import owner_notifications
from owner_crm.tests import sample_merge_vars
from owner_crm.tests.test_services import test_message


class TestOnboardingOwnerNotifications(TestCase):
    @freeze_time("2014-10-10 9:55:00")
    def setUp(self):
        from owner_crm.models import Campaign
        campaign = owner_crm.factories.Campaign.create(
            name='owner_notifications.FirstOnboardingReminder',
            preferred_medium=Campaign.SMS_MEDIUM,
        )
        campaign = owner_crm.factories.Campaign.create(
            name='owner_notifications.SecondOnboardingReminder',
            preferred_medium=Campaign.SMS_MEDIUM,
        )
        campaign = owner_crm.factories.Campaign.create(
            name='owner_notifications.ThirdOnboardingReminder',
            preferred_medium=Campaign.SMS_MEDIUM,
        )
        campaign = owner_crm.factories.Campaign.create(
            name='owner_notifications.FourthOnboardingReminder',
            preferred_medium=Campaign.SMS_MEDIUM,
        )

    def test_onboarding_owner_gets_email(self):
        from idlecars import sms_service
        sms_service.test_reset()

        server.models.OnboardingOwner.objects.create(
            phone_number='1234567890',
            name='Elmi bot'
        )

        owner_service.process_onboarding_reminder()

        self.assertEqual(len(sms_service.test_get_outbox()), 1)
        self.assertTrue('looking to rent your car' in sms_service.test_get_outbox()[0]['body'])

    def test_no_email_twice(self):
        from idlecars import sms_service
        sms_service.test_reset()

        server.models.OnboardingOwner.objects.create(
            phone_number='1234567890',
            name='Elmi bot'
        )

        owner_service.process_onboarding_reminder()
        owner_service.process_onboarding_reminder()

        self.assertEqual(len(sms_service.test_get_outbox()), 1)

    def test_no_email_to_converted_owner(self):
        from idlecars import sms_service
        sms_service.test_reset()

        exisiting_owner = server.factories.Owner.create()

        server.models.OnboardingOwner.objects.create(
            phone_number=exisiting_owner.auth_users.first().username,
            name='Elmi bot'
        )

        owner_service.process_onboarding_reminder()

        self.assertEqual(len(sms_service.test_get_outbox()), 0)

    def test_no_email_early(self):
        from idlecars import sms_service
        sms_service.test_reset()

        with freeze_time("2014-10-10 9:55:00"):
            server.models.OnboardingOwner.objects.create(
                phone_number='1234567890',
                name='Elmi bot'
            )
        with freeze_time("2014-10-10 10:00:00"):
            owner_service.process_onboarding_reminder()
        with freeze_time("2014-10-12 10:00:00"):
            owner_service.process_onboarding_reminder()

        self.assertEqual(len(sms_service.test_get_outbox()), 1)

    def test_no_email_late(self):
        from idlecars import sms_service
        sms_service.test_reset()

        with freeze_time("2014-10-10 9:55:00"):
            server.models.OnboardingOwner.objects.create(
                phone_number='1234567890',
                name='Elmi bot'
            )
        with freeze_time("2015-10-10 10:00:00"):
            owner_service.process_onboarding_reminder()

        self.assertEqual(len(sms_service.test_get_outbox()), 4)

    def test_all_onboarding_emails(self):
        from idlecars import sms_service
        sms_service.test_reset()

        with freeze_time("2014-10-10 9:55:00"):
            server.models.OnboardingOwner.objects.create(
                phone_number='1234567890',
                name='Elmi bot'
            )
        with freeze_time("2014-10-10 10:00:00"):
            owner_service.process_onboarding_reminder()
        with freeze_time("2014-10-17 10:00:00"):
            owner_service.process_onboarding_reminder()
        with freeze_time("2014-10-24 10:00:00"):
            owner_service.process_onboarding_reminder()
        with freeze_time("2014-10-31 10:00:00"):
            owner_service.process_onboarding_reminder()

        self.assertEqual(len(sms_service.test_get_outbox()), 4)


class TestOwnerPendingBookingNotifications(TestCase):
    @freeze_time("2014-10-10 9:55:00")
    def setUp(self):
        self.driver = server.factories.Driver.create()

    def test_only_required_bookings_send_emails(self):
        with freeze_time("2014-10-10 11:00:00"):
            good_booking = server.factories.Booking.create(driver=self.driver)
            server.factories.Booking.create()
            server.factories.ReservedBooking.create(driver=self.driver)
            server.factories.RequestedBooking.create(driver=self.driver)
            server.factories.AcceptedBooking.create(driver=self.driver)
            server.factories.BookedBooking.create(driver=self.driver)
            server.factories.ReturnedBooking.create(driver=self.driver)
            server.factories.RefundedBooking.create(driver=self.driver)
            server.factories.IncompleteBooking.create(driver=self.driver)

        owner_service.process_pending_booking_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        self.assertEqual(
            outbox[0].subject,
            'Someone is interested in your {}'.format(good_booking.car.display_name()),
        )

    def test_no_email_twice(self):
        with freeze_time("2014-10-10 11:00:00"):
            good_booking = server.factories.Booking.create(driver=self.driver)

        owner_service.process_pending_booking_reminder()
        owner_service.process_pending_booking_reminder()

    @freeze_time("2014-10-11 10:55:00")
    def test_no_email_early(self):
        with freeze_time("2014-10-10 11:00:00"):
            good_booking = server.factories.Booking.create(driver=self.driver)

        owner_service.process_pending_booking_reminder()


class TestOwnerAccountNotification(TestCase):
    def test_no_car_no_email(self):
        with freeze_time("2014-10-10 11:00:00"):
            complete_owner = server.factories.PendingOwner.create()

        owner_service.process_account_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    @freeze_time("2014-10-11 12:00:00")
    def test_only_incomplete_owners_get_reminder(self):
        with freeze_time("2014-10-10 11:00:00"):
            missing_zipcode_owner = server.factories.BankAccountOwner.create()
            missing_zipcode_owner.zipcode = ''
            missing_zipcode_owner.save()
            missing_bank_account_owner = server.factories.Owner.create()
            complete_owner = server.factories.PendingOwner.create()

            server.factories.ClaimedCar.create(owner=missing_zipcode_owner)
            server.factories.ClaimedCar.create(owner=missing_bank_account_owner)
            server.factories.ClaimedCar.create(owner=complete_owner)

        owner_service.process_account_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        self.assertEqual(
            outbox[0].subject,
            'Your account is incomplete and your cars are not listed'
        )

        self.assertFalse(
            complete_owner.email() in [outbox[1].merge_vars.keys()[0], outbox[0].merge_vars.keys()[0]]
        )

    @freeze_time("2014-10-11 12:00:00")
    def test_no_email_twice(self):
        with freeze_time("2014-10-10 11:00:00"):
            missing_bank_account_owner = server.factories.Owner.create()
            server.factories.ClaimedCar.create(owner=missing_bank_account_owner)

        owner_service.process_account_reminder()
        owner_service.process_account_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_no_email_early(self):
        missing_bank_account_owner = server.factories.Owner.create()
        server.factories.ClaimedCar.create(owner=missing_bank_account_owner)

        owner_service.process_account_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_second_reminder(self):
        with freeze_time("2014-10-10 11:00:00"):
            missing_bank_account_owner = server.factories.Owner.create()
            server.factories.ClaimedCar.create(owner=missing_bank_account_owner)

        owner_service.process_account_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        self.assertEqual(
            outbox[1].subject,
            'Your cars are not listed on Idlecars yet! Complete your account today!'
        )


class TestOwnerRenewalNotifications(TestCase):
    def _setup_car_with_update_time(self, update_time):
        car = server.factories.BookableCar.create(
            last_status_update=update_time,
        )
        return car

    def _update_time_about_to_go_stale(self):
        return timezone.now() - (timedelta(days=settings.STALENESS_LIMIT) - timedelta(hours=1))

    def test_whole_enchilada(self):
        last_update = self._update_time_about_to_go_stale()

        cars = []
        for i in xrange(2):  # two cars about to go stale
            cars.append(self._setup_car_with_update_time(last_update))

        # one car just renewed to make sure filtering is working
        self._setup_car_with_update_time(timezone.now())

        owner_service.process_renewal_reminder()

        # check what got sent
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

        subjects = [m.subject for m in outbox]
        for car in cars:
            self.assertTrue('Your {} listing is about to expire.'.format(car.display_name()) in subjects)

        # validate that the merge vars are being set correctly:
        for message in outbox:
            email = message.merge_vars.keys()[0]
            user = User.objects.get(email=email)
            car = server.models.Owner.objects.get(auth_users=user).cars.all()[0]
            var = message.merge_vars[email]

            self.assertEqual(var['CTA_LABEL'], 'Update Listing Now')
            self.assertEqual(var['CTA_URL'], idlecars.app_routes_owner.car_details_url(car))
            self.assertEqual(var['FNAME'], user.first_name)
            self.assertTrue(car.plate in var['TEXT'])
            self.assertTrue(car.display_name() in var['TEXT'])

    def test_renewable_cars(self):
        last_update = self._update_time_about_to_go_stale()
        car = self._setup_car_with_update_time(last_update)
        owner_service.process_renewal_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1) # we sent an email about this car

        # Make sure the car that we just emailed about don't get a second email
        owner_service.process_renewal_reminder()
        self.assertEqual(len(outbox), 1)

        # if we sent them a message last time it was about to go stale, we message them again
        msg_record = owner_crm.models.Message.objects.get(car=car)
        msg_record.created_time = timezone.now() - timedelta(days=5)
        msg_record.save()
        owner_service.process_renewal_reminder()
        self.assertEqual(len(outbox), 2)


class TestOwnerInsuranceNotifications(TestCase):
    def _new_requested_booking(self, create_time):
        with freeze_time(create_time):
            return server.factories.RequestedBooking.create()

    @freeze_time(timezone.datetime(2014, 10, 11, 10, 00, 00, tzinfo=timezone.get_current_timezone()))
    def test_owner_reminder(self):
        self.booking = self._new_requested_booking("2014-10-10 18:00:00")

        owner_service.process_insurance_reminder()
        test_message.verify_throttled_on_owner(
            self.booking.car.owner,
            'first_morning_insurance_reminder'
        )

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))
        self.assertEqual(
            outbox[0].subject,
            'Has {} been accepted on the {}?'.format(
                self.booking.driver.full_name(),
                self.booking.car.display_name()
            )
        )


    @freeze_time(timezone.datetime(2014, 10, 11, 10, tzinfo=timezone.get_current_timezone()))
    def test_no_booking(self):
        owner_service.process_insurance_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    @freeze_time(timezone.datetime(2014, 10, 11, 10, tzinfo=timezone.get_current_timezone()))
    def test_no_email_twice(self):
        booking_time = timezone.datetime(2014, 10, 10, 18, tzinfo=timezone.get_current_timezone())
        self.booking = self._new_requested_booking(booking_time)

        owner_service.process_insurance_reminder()
        test_message.verify_throttled_on_owner(
            self.booking.car.owner,
            'first_morning_insurance_reminder',
        )
        owner_service.process_insurance_reminder()

        # we should have sent only one reminder about getting the driver on the insurance.
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_only_requested_bookings_send_reminder(self):
        tz = timezone.get_current_timezone()
        with freeze_time(timezone.datetime(2014, 10, 11, 18, 00, 00, tzinfo=tz)):
            server.factories.Booking.create()
            server.factories.ReservedBooking.create()
            server.factories.AcceptedBooking.create()
            server.factories.BookedBooking.create()
            server.factories.ReturnedBooking.create()
            server.factories.RefundedBooking.create()
            server.factories.IncompleteBooking.create()

        with freeze_time(timezone.datetime(2014, 10, 11, 10, tzinfo=timezone.get_current_timezone())):
            owner_service.process_insurance_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_reminder_emails_morning_until_failure(self):
        tz = timezone.get_current_timezone()
        self.booking = self._new_requested_booking(timezone.datetime(2014, 10, 10, 18, tzinfo=tz)) # UTC

        with freeze_time(timezone.datetime(2014, 10, 11, 10, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')
            test_message.verify_throttled_on_owner(
                self.booking.car.owner,
                'first_morning_insurance_reminder'
            )

        with freeze_time(timezone.datetime(2014, 10, 11, 13, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 12, 10, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')
            test_message.verify_throttled_on_owner(
                self.booking.car.owner,
                'second_morning_insurance_reminder'
            )

        with freeze_time(timezone.datetime(2014, 10, 12, 13, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 13, 10, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 13, 13, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 13, 18, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')

        '''
            - message to owner: first morning reminder
            - message to owner: first afternoon reminder
            - message to owner: second morning reminder
            - message to owner: second afternoon reminder
            - message to owner: third morning reminder
            - message to owner: third afternoon reminder
            - message to owner: insurance too slow reminder
            - message to driver: insurance failed reminder
        '''
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 8)

    def test_reminder_emails_afternoon_until_failure(self):
        tz = timezone.get_current_timezone()
        self.booking = self._new_requested_booking(timezone.datetime(2014, 10, 10, 0, tzinfo=tz))

        with freeze_time(timezone.datetime(2014, 10, 10, 13, tzinfo=tz)):

            owner_service.process_insurance_reminder()
            call_command('cron_job')
            test_message.verify_throttled_on_owner(
                self.booking.car.owner,
                'first_afternoon_insurance_reminder'
            )
        with freeze_time(timezone.datetime(2014, 10, 11, 10, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 11, 13, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')
            test_message.verify_throttled_on_owner(
                self.booking.car.owner,
                'second_afternoon_insurance_reminder'
            )

        with freeze_time(timezone.datetime(2014, 10, 12, 10, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 12, 13, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 13, 0, tzinfo=tz)):
            owner_service.process_insurance_reminder()
            call_command('cron_job')

        '''
            - message to owner: first afternoon reminder
            - message to owner: first morning reminder
            - message to owner: second afternoon reminder
            - message to owner: second morning reminder
            - message to owner: third afternoon reminder
            - message to owner: insurance too slow reminder
            - message to driver: insurance failed reminder
        '''
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 7)


class TestOwnerPickupNotifications(TestCase):
    @freeze_time("2014-10-10 9:55:00")
    def setUp(self):
        self.accepted_booking = server.factories.AcceptedBooking.create()

    def test_only_accepted_bookings_has_reminder(self):
        with freeze_time("2014-10-10 9:55:00"):
            server.factories.Booking.create()
            server.factories.ReservedBooking.create()
            server.factories.RequestedBooking.create()
            server.factories.BookedBooking.create()
            server.factories.ReturnedBooking.create()
            server.factories.RefundedBooking.create()
            server.factories.IncompleteBooking.create()

        with freeze_time("2014-10-10 11:00:00"):
            owner_service.process_pickup_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            '{} will schedule pickup soon'.format(self.accepted_booking.driver.full_name()),
        )

    def test_no_email_twice(self):
        with freeze_time("2014-10-10 11:00:00"):
            owner_service.process_pickup_reminder()
            owner_service.process_pickup_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_no_email_early(self):
        with freeze_time("2014-10-10 10:00:00"):
            owner_service.process_pickup_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_no_email_after_pickup(self):
        with freeze_time("2014-10-10 11:00:00"):
            self.accepted_booking.pickup_time = timezone.now()
            self.accepted_booking.save()
            owner_service.process_pickup_reminder()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_second_reminder(self):
        with freeze_time("2014-10-10 10:00:00"):
            owner_service.process_pickup_reminder()
        with freeze_time("2014-10-10 22:00:00"):
            owner_service.process_pickup_reminder()

        '''
            - message to owner: first pickup reminder
            - message to owner: second pickup reminder
        '''
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)
        self.assertEqual(
            outbox[1].subject,
            '{} will schedule pickup soon'.format(self.accepted_booking.driver.full_name()),
        )


class TestOwnerExtendRentalNotifications(TestCase):
    def _create_booking_and_change_end_time(self, booking_type):
        with freeze_time("2014-10-10 9:00:00"):
            booking = getattr(server.factories, booking_type).create()
        booking_service.set_end_time(booking, timezone.now())
        return booking

    def test_end_time_changed(self):
        booking = self._create_booking_and_change_end_time('BookedBooking')
        self._create_booking_and_change_end_time('Booking')
        self._create_booking_and_change_end_time('ReservedBooking')
        self._create_booking_and_change_end_time('RequestedBooking')
        self._create_booking_and_change_end_time('ReturnedBooking')
        self._create_booking_and_change_end_time('RefundedBooking')
        self._create_booking_and_change_end_time('IncompleteBooking')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'The rental for your {} ({}) was extended until {}'.format(
                booking.car.display_name(),
                booking.car.plate,
                booking.end_time.strftime('%b %d'),
            ),
        )

    def test_no_email_at_booking_creation(self):
        booking = server.factories.BookedBooking.create()
        self.assertTrue(booking.end_time != None)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_no_email_at_end_time_to_None(self):
        booking = server.factories.BookedBooking.create()
        booking.end_time = None
        booking.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_more_than_one_email(self):
        booking = self._create_booking_and_change_end_time('BookedBooking')
        booking_service.set_end_time(booking, timezone.now())

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)
