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
        self.car = factories.BookableCar.create(
            owner=owner,
            make_model=make_model,
            status='available',
            next_available_date=timezone.now() + datetime.timedelta(days=1),
            min_lease='_03_two_weeks',
            hybrid=True,
        )

    def test_create_pending_booking(self):
        driver = factories.Driver.create()
        new_booking = booking_service.create_booking(self.car, driver)
        self.assertIsNotNone(new_booking)
        self.assertEqual(new_booking.driver, driver)
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.get_state(), models.Booking.PENDING)

        # we should NOT have sent an email to ops telling them about the new booking
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def _validate_requested_messages(self, booking, outbox):
        '''
        Validate that the right messages were sent when a booking has been requested.
        '''
        self.assertEqual(len(outbox), 2)

        # an email to the owner to get the driver on insurance
        self.assertEqual(outbox[0].merge_vars.keys()[0], booking.car.owner.email())
        self.assertEqual(
            outbox[0].subject,
            'A driver has booked your {}.'.format(booking.car.display_name())
        )

        # an email to the driver that insurance is in progress
        self.assertEqual(outbox[1].merge_vars.keys()[0], booking.driver.email())
        self.assertEqual(
            outbox[1].subject,
            'Congratulations! Your documents have been submitted!'
        )

        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_create_booking_docs_complete(self):
        driver = factories.CompletedDriver.create()
        new_booking = booking_service.create_booking(self.car, driver)
        self.assertEqual(new_booking.driver, driver)
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.get_state(), models.Booking.REQUESTED)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        self._validate_requested_messages(new_booking, outbox)

    def _validate_missed_plus_requested_msgs(self, new_booking, other_booking, outbox):
        self.assertEqual(len(outbox), 4)

        # an email to the other driver to know their car is no longer available
        self.assertEqual(outbox[0].merge_vars.keys()[0], other_booking.driver.email())
        self.assertEqual(
            outbox[0].subject,
            'Someone else rented your {}.'.format(other_booking.car.display_name())
        )

        self._validate_requested_messages(new_booking, outbox[1:])

    def test_on_insurance_approved(self):
        booking = factories.RequestedBooking.create()
        booking.approval_time = timezone.now()
        booking.clean()
        booking.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'Alright! Your {} is ready to pick up!'.format(booking.car.display_name())
        )

    def _create_incomplete_booking(self, reason):
        booking = factories.RequestedBooking.create()
        booking.incomplete_time = timezone.now()
        booking.incomplete_reason = reason
        booking.clean()
        booking.save()
        return booking

    def test_insurance_rejected(self):
        booking = self._create_incomplete_booking(models.Booking.REASON_OWNER_REJECTED)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'You couldn\'t be added to the insurance on the car you wanted'
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_insurance_failed(self):
        booking = self._create_incomplete_booking(models.Booking.REASON_OWNER_TOO_SLOW)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)
        # we should have sent an email to owner because owner too slow
        self.assertEqual(
             outbox[0].subject,
            'Your {} rental has been canceled'.format(booking.car.display_name())
        )
        # we should have sent an email to driver because owner too slow
        self.assertEqual(
            outbox[1].subject,
            'We were unable to complete your {} booking'.format(booking.car.display_name())
        )

    def test_driver_rejected(self):
        booking = self._create_incomplete_booking(models.Booking.REASON_DRIVER_REJECTED)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
             outbox[0].subject,
            'Your {} rental has canceled.'.format(booking.car.display_name())
        )

    def test_car_rented_elsewhere(self):
        booking = self._create_incomplete_booking(models.Booking.REASON_MISSED)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
             outbox[0].subject,
            'Sorry, someone else rented out the car you wanted.'
        )


    def test_cancel_pending_booking(self):
        driver = factories.Driver.create()
        new_booking = booking_service.create_booking(self.car, driver)
        booking_service.cancel(new_booking)

        ''' we should have sent
        - one email to the driver to confirm the booking was canceled.
        '''
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'Confirmation: Your rental has been canceled.'
        )

    def test_cancel_requested_booking(self):
        approved_driver = factories.BaseLetterDriver.create()
        new_booking = booking_service.create_booking(self.car, approved_driver)
        booking_service.cancel(new_booking)

        ''' we should have sent
        - message to the owner to send the insurance docs,
        - message to the driver to notify the booking was sent to insurance,
        - message to the owner to cancel the insurance request.
        - message to the driver to confirm the booking was canceled,
        '''
        expected_email_count = 4
        from django.core.mail import outbox
        if not len(outbox) == expected_email_count:
            print [o.subject for o in outbox]
        self.assertEqual(len(outbox), expected_email_count)

        self.assertEqual(
            outbox[2].subject,
            'Confirmation: Your rental has been canceled.'
        )
        self.assertEqual(
            outbox[3].subject,
            'Your {} rental has canceled.'.format(new_booking.car.display_name())
        )

    def test_booking_return(self):
        booking = factories.BookedBooking.create()
        self.assertEqual(1, booking_service.filter_active(models.Booking.objects.all()).count())
        booking_service.booking_return(booking)
        self.assertEqual(1, booking_service.filter_returned(models.Booking.objects.all()).count())

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'Has your {} been returned?'.format(booking.car.display_name())
        )

    def test_no_active_no_return(self):
        booking = factories.AcceptedBooking.create()
        with self.assertRaises(Exception):
            booking_service.booking_return(booking)
        self.assertEqual(0, booking_service.filter_returned(models.Booking.objects.all()).count())

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_removed_from_car(self):
        booking = factories.ReturnedBooking.create()
        self.assertEqual(1, booking_service.filter_returned(models.Booking.objects.all()).count())
        booking_service.return_confirm(booking)
        self.assertEqual(1, booking_service.filter_refunded(models.Booking.objects.all()).count())

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'You\'re removed from the {}.'.format(booking.car.display_name())
        )
