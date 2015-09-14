# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase
from django.conf import settings

from server.services import booking as booking_service
from server.services import driver as driver_service
from server import factories, models

from owner_crm.tests import sample_merge_vars


class BookingServiceTest(TestCase):
    def setUp(self):
        owner = factories.Owner.create(state_code='NY')
        make_model = factories.MakeModel.create()
        self.car = factories.Car.create(
            owner=owner,
            make_model=make_model,
            status='available',
            next_available_date=timezone.now().date() + datetime.timedelta(days=1),
            min_lease='_03_two_weeks',
            hybrid=True,
        )

    def _validate_new_booking_email(self, email, booking):
        self.assertEqual(
            email.subject,
            'New Booking from {}'.format(booking.driver.phone_number())
        )
        self.assertEqual(email.merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(
            email.merge_vars[settings.OPS_EMAIL]['CTA_URL'].split('/')[-2],
            unicode(booking.pk),
        )

    def test_create_pending_booking(self):
        driver = factories.Driver.create()
        new_booking = booking_service.create_booking(self.car, driver)
        self.assertIsNotNone(new_booking)
        self.assertEqual(new_booking.driver, driver)
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.get_state(), models.Booking.PENDING)

        # we should have sent an email to ops telling them about the new booking
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self._validate_new_booking_email(outbox[0], new_booking)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_create_booking_docs_complete(self):
        driver = factories.CompletedDriver.create()
        new_booking = booking_service.create_booking(self.car, driver)
        self.assertEqual(new_booking.get_state(), models.Booking.PENDING)

        # we should have sent an email to ops telling them about the new booking
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self._validate_new_booking_email(outbox[0], new_booking)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_create_booking_docs_approved(self):
        driver = factories.ApprovedDriver.create()
        new_booking = booking_service.create_booking(self.car, driver)
        self.assertEqual(new_booking.driver, driver)
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.get_state(), models.Booking.PENDING)

        # check we sent the right email
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self._validate_new_booking_email(outbox[0], new_booking)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_checkout_all_docs_uploaded(self):
        # TODO
        pass

    def test_checkout_docs_approved(self):
        # TODO
        pass

    def test_checkout_with_others_too_slow(self):
        # set up the other driver, and create a booking for them
        other_driver = factories.Driver.create()
        booking_service.create_booking(self.car, other_driver)

        driver = factories.ApprovedDriver.create()
        new_booking = booking_service.create_booking(self.car, driver)
        new_booking = booking_service.checkout(new_booking)
        self.assertEqual(new_booking.get_state(), models.Booking.REQUESTED)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 4)

        # two emails to support that there are new bookings
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(outbox[0].subject, 'New Booking from {}'.format(other_driver.phone_number()))
        self.assertEqual(outbox[1].subject, 'New Booking from {}'.format(driver.phone_number()))

        # an email to the other driver to know their car is no longer available
        self.assertEqual(outbox[2].merge_vars.keys()[0], other_driver.email())
        self.assertEqual(
            outbox[2].subject,
            'Someone else rented your {}.'.format(new_booking.car.display_name())
        )

        # an email to the owner to get the driver on insurance
        self.assertEqual(outbox[3].merge_vars.keys()[0], new_booking.car.owner.email())
        self.assertEqual(
            outbox[3].subject,
            'A driver has booked your {}.'.format(new_booking.car.display_name())
        )

        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_cancel_pending_booking(self):
        driver = factories.Driver.create()
        new_booking = booking_service.create_booking(self.car, driver)
        booking_service.cancel(new_booking)

        ''' we should have sent
        - one email to ops when the booking was created,
        - one email to ops when the booking was canceled,
        - one emial to the driver to confirm the booking was canceled.
        '''
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 3)

    def test_cancel_requested_booking(self):
        approved_driver = factories.ApprovedDriver.create()
        new_booking = booking_service.create_booking(self.car, approved_driver)
        new_booking = booking_service.checkout(new_booking)
        booking_service.cancel(new_booking)

        ''' we should have sent
        - message to ops about the initial booking
        - message to the owner to send the insurance docs,
        - message to the owner to cancel the insurance request.
        - message to ops when the booking was canceled,
        - message to the driver to confirm the booking was canceled,
        '''
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 5)

    def test_correct_start_time(self):
        driver = factories.Driver.create()
        new_booking = booking_service.create_booking(self.car, driver)

        est_time = timezone.now() + datetime.timedelta(days=2)
        time_string = est_time.strftime('%b %d')
        self.assertEqual(booking_service.start_time_display(new_booking), time_string)

        # make sure the estimated time is correct after the checkout is copmlete
        new_booking.checkout_time = datetime.datetime(2015, 8, 15, 8, 15, 12, 0, timezone.get_current_timezone())
        self.assertEqual(booking_service.start_time_display(new_booking), 'Aug 17')

        # make sure the driver sees the rental starts 'on pickup' once they're approved
        new_booking.approval_time = datetime.datetime(2015, 8, 17, 8, 15, 12, 0, timezone.get_current_timezone())
        self.assertEqual(booking_service.start_time_display(new_booking), 'on pickup')

        # make sure the driver sees the rental starts 'on pickup' once they're approved
        new_booking.pickup_time = datetime.datetime(2015, 8, 18, 8, 15, 12, 0, timezone.get_current_timezone())
        self.assertEqual(booking_service.start_time_display(new_booking), 'Aug 18')
