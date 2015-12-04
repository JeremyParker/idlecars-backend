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

class TestOwnerNotifications(TestCase):
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

        call_command('owner_notifications')

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
        owner_service._renewal_email()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1) # we sent an email about this car

        # Make sure the car that we just emailed about don't get a second email
        owner_service._renewal_email()
        self.assertEqual(len(outbox), 1)

        # if we sent them a message last time it was about to go stale, we message them again
        msg_record = owner_crm.models.Message.objects.get(car=car)
        msg_record.created_time = timezone.now() - timedelta(days=5)
        msg_record.save()
        owner_service._renewal_email()
        self.assertEqual(len(outbox), 2)

    def _new_requested_booking(self, create_time):
        with freeze_time(create_time):
            return server.factories.RequestedBooking.create()

    @freeze_time(timezone.datetime(2014, 10, 11, 10, 00, 00, tzinfo=timezone.get_current_timezone()))
    def test_owner_reminder(self):
        self.booking = self._new_requested_booking("2014-10-10 18:00:00")

        call_command('owner_notifications')
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
        call_command('owner_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    @freeze_time(timezone.datetime(2014, 10, 11, 10, tzinfo=timezone.get_current_timezone()))
    def test_no_email_twice(self):
        booking_time = timezone.datetime(2014, 10, 10, 18, tzinfo=timezone.get_current_timezone())
        self.booking = self._new_requested_booking(booking_time)

        call_command('owner_notifications')
        test_message.verify_throttled_on_owner(
            self.booking.car.owner,
            'first_morning_insurance_reminder',
        )
        call_command('owner_notifications')

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
            call_command('owner_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_reminder_emails_morning_until_failure(self):
        tz = timezone.get_current_timezone()
        self.booking = self._new_requested_booking("2014-10-10 18:00:00") # UTC

        with freeze_time(timezone.datetime(2014, 10, 11, 10, tzinfo=tz)):
            call_command('owner_notifications')
            call_command('cron_job')
            test_message.verify_throttled_on_owner(
                self.booking.car.owner,
                'first_morning_insurance_reminder'
            )

        with freeze_time(timezone.datetime(2014, 10, 11, 17, tzinfo=tz)):
            call_command('owner_notifications')
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 12, 10, tzinfo=tz)):
            call_command('owner_notifications')
            call_command('cron_job')
            test_message.verify_throttled_on_owner(
                self.booking.car.owner,
                'second_morning_insurance_reminder'
            )

        with freeze_time(timezone.datetime(2014, 10, 12, 17, tzinfo=tz)):
            call_command('owner_notifications')
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 13, 10, tzinfo=tz)):
            call_command('owner_notifications')
            call_command('cron_job')

        # the final cancelation of the booking happens through the Admin, which triggers this:
        original_state = self.booking.get_state()
        self.booking.incomplete_time = timezone.now()
        self.booking.incomplete_reason = server.models.Booking.REASON_OWNER_TOO_SLOW
        booking_service.on_incomplete(self.booking, original_state)
        self.booking.save()

        '''
            - message to owner: first morning reminder
            - message to owner: first afternoon reminder
            - message to owner: second morning reminder
            - message to owner: second afternoon reminder
            - message to owner: insurance too slow reminder
            - message to driver: insurance failed reminder
        '''
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 6)

    def test_reminder_emails_afternoon_until_failure(self):
        tz = timezone.get_current_timezone()
        self.booking = self._new_requested_booking(timezone.datetime(2014, 10, 10, 23, tzinfo=tz))

        with freeze_time(timezone.datetime(2014, 10, 11, 17, tzinfo=tz)):
            call_command('owner_notifications')
            call_command('cron_job')
            test_message.verify_throttled_on_owner(
                self.booking.car.owner,
                'first_afternoon_insurance_reminder'
            )

        with freeze_time(timezone.datetime(2014, 10, 12, 10, tzinfo=tz)):
            call_command('owner_notifications')
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 12, 17, tzinfo=tz)):
            call_command('owner_notifications')
            call_command('cron_job')
            test_message.verify_throttled_on_owner(
                self.booking.car.owner,
                'second_afternoon_insurance_reminder'
            )

        with freeze_time(timezone.datetime(2014, 10, 13, 10, tzinfo=tz)):
            call_command('owner_notifications')
            call_command('cron_job')

        with freeze_time(timezone.datetime(2014, 10, 13, 17, tzinfo=tz)):
            call_command('owner_notifications')
            call_command('cron_job')

        # the final cancelation of the booking happens through the Admin, which triggers this:
        original_state = self.booking.get_state()
        self.booking.incomplete_time = timezone.now()
        self.booking.incomplete_reason = server.models.Booking.REASON_OWNER_TOO_SLOW
        booking_service.on_incomplete(self.booking, original_state)
        self.booking.save()

        '''
            - message to owner: first morning reminder
            - message to owner: first afternoon reminder
            - message to owner: second morning reminder
            - message to owner: second afternoon reminder
            - message to owner: insurance too slow reminder
            - message to driver: insurance failed reminder
        '''
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 6)
