# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase
from django.conf import settings

from server.services import booking as booking_service
from server.services import driver as driver_service
from server import factories, models, payment_gateways

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
        driver = factories.PaymentMethodDriver.create()
        new_booking = factories.Booking.create(car=self.car, driver=driver)

        # checkout
        new_booking = booking_service.checkout(new_booking)
        self.assertEqual(new_booking.get_state(), models.Booking.RESERVED)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))
        # TODO - make sure this is the right email to the right person

        # there should be a single payment that is in the pre-authorized state
        self.assertEqual(len(new_booking.payment_set.all()), 1)
        self.assertEqual(new_booking.payment_set.last().status, models.Payment.PRE_AUTHORIZED)

    def _checkout_approved_driver(self):
        driver = factories.BaseLetterDriver.create()
        new_booking = factories.Booking.create(car=self.car, driver=driver)
        new_booking = booking_service.checkout(new_booking)
        self.assertEqual(new_booking.get_state(), models.Booking.REQUESTED)
        self.assertEqual(len(new_booking.payment_set.all()), 1)
        self.assertEqual(len(new_booking.payment_set.filter(status=models.Payment.PRE_AUTHORIZED)), 1)
        self.assertEqual(new_booking.payment_set.last().amount, new_booking.car.solo_deposit)
        return new_booking

    def test_checkout_receipt(self):
        driver = factories.ApprovedDriver.create()
        new_booking = factories.Booking.create(car=self.car, driver=driver)
        new_booking = booking_service.checkout(new_booking)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

    def test_checkout_docs_approved(self):
        new_booking = self._checkout_approved_driver()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        # an email to the owner to get the driver on insurance
        self.assertEqual(outbox[0].merge_vars.keys()[0], new_booking.car.owner.email())
        self.assertEqual(
            outbox[0].subject,
            'A driver has booked your {}.'.format(new_booking.car.display_name())
        )

        # an email to the driver that insurance is in progress
        self.assertEqual(outbox[1].merge_vars.keys()[0], new_booking.driver.email())
        self.assertEqual(
            outbox[1].subject,
            'Congratulations! Your documents have been submitted!'
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_checkout_with_others_too_slow(self):
        # set up the other driver, and create a booking for them
        other_driver = factories.Driver.create()
        factories.Booking.create(car=self.car, driver=other_driver)

        new_booking = self._checkout_approved_driver()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 3)

        # an email to the other driver to know their car is no longer available
        self.assertEqual(outbox[0].merge_vars.keys()[0], other_driver.email())
        self.assertEqual(
            outbox[0].subject,
            'Someone else rented your {}.'.format(new_booking.car.display_name())
        )

        # an email to the owner to get the driver on insurance
        self.assertEqual(outbox[1].merge_vars.keys()[0], new_booking.car.owner.email())
        self.assertEqual(
            outbox[1].subject,
            'A driver has booked your {}.'.format(new_booking.car.display_name())
        )

        # an email to the driver that insurance is in progress
        self.assertEqual(outbox[2].merge_vars.keys()[0], new_booking.driver.email())
        self.assertEqual(
            outbox[2].subject,
            'Congratulations! Your documents have been submitted!'
        )

        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def _check_payments_after_pickup(self, new_booking):
        self.assertEqual(len(new_booking.payment_set.filter(status=models.Payment.HELD_IN_ESCROW)), 1)
        self.assertEqual(len(new_booking.payment_set.filter(status=models.Payment.SETTLED)), 1)
        first_week_rent_payment = new_booking.payment_set.filter(status=models.Payment.SETTLED)[0]
        self.assertEqual(first_week_rent_payment.amount, new_booking.weekly_rent)

    def test_pickup(self):
        driver = factories.PaymentMethodDriver.create()
        new_booking = factories.AcceptedBooking.create(car=self.car, driver=driver)

        # pick up the car
        new_booking = booking_service.pickup(new_booking)

        self.assertEqual(new_booking.get_state(), models.Booking.ACTIVE)
        self._check_payments_after_pickup(new_booking)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        # a pickup confirmation to owner
        self.assertEqual(
            outbox[0].subject,
            'You are ready to drive!'
        )

        # a pickup confirmation to driver
        self.assertEqual(
            outbox[1].subject,
            '{} has paid you for the {}'.format(new_booking.driver.full_name(), new_booking.car.display_name()),
        )

    def test_pickup_after_failure(self):
        driver = factories.PaymentMethodDriver.create()
        new_booking = factories.AcceptedBooking.create(car=self.car, driver=driver)
        self.assertEqual(new_booking.get_state(), models.Booking.ACCEPTED)
        self.assertEqual(len(new_booking.payment_set.all()), 1)
        self.assertEqual(new_booking.payment_set.first().status, models.Payment.PRE_AUTHORIZED)

        # fail to pick up the car
        next_response = (models.Payment.DECLINED, 'This transaction was declined for some reason.',)
        gateway = payment_gateways.get_gateway('fake').next_payment_response.append(next_response)
        with self.assertRaises(booking_service.BookingError):
            new_booking = booking_service.pickup(new_booking)
        new_booking.refresh_from_db()  # make sure our local copy is fresh. pickup() changed it.

        # make sure there's a declined payment in there
        self.assertTrue(models.Payment.DECLINED in [p.status for p in new_booking.payment_set.all()])

        # successfully pick up the car
        new_booking = booking_service.pickup(new_booking)
        self._check_payments_after_pickup(new_booking)

    def test_base_letter_approved_no_booking(self):
        self.driver = factories.ApprovedDriver.create()
        self.assertFalse(self.driver.base_letter_rejected)
        self.assertEqual(self.driver.base_letter, '')

        self.driver.base_letter = 'some base letter'
        self.driver.clean()
        self.driver.save()

        # we should have sent driver an email telling them about the to book a car
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        self.assertEqual(outbox[0].merge_vars.keys()[0], self.driver.email())
        self.assertEqual(
            outbox[0].subject,
            'Welcome to idlecars, {}!'.format(self.driver.full_name())
        )

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
        approved_driver = factories.BaseLetterDriver.create()
        new_booking = booking_service.create_booking(self.car, approved_driver)
        new_booking = booking_service.checkout(new_booking)
        booking_service.cancel(new_booking)

        # make sure the pre-authorized payment got voided
        self.assertEqual(len(new_booking.payment_set.all()), 1)
        self.assertEqual(new_booking.payment_set.last().status, models.Payment.VOIDED)

        ''' we should have sent
        - message to ops about the initial booking
        - message to the owner to send the insurance docs,
        - message to the driver to notify the booking was sent to insurance,
        - message to the owner to cancel the insurance request.
        - message to ops when the booking was canceled,
        - message to the driver to confirm the booking was canceled,
        '''
        from django.core.mail import outbox
        if not len(outbox) == 6:
            print [o.subject for o in outbox]
        self.assertEqual(len(outbox), 6)

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
