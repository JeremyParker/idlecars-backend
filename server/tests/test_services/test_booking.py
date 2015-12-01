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

    def test_create_booking_docs_complete(self):
        driver = factories.CompletedDriver.create()
        new_booking = booking_service.create_booking(self.car, driver)
        self.assertEqual(new_booking.get_state(), models.Booking.PENDING)

        # we should NOT have sent an email to ops telling them about the new booking
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)

    def test_create_booking_docs_approved(self):
        driver = factories.ApprovedDriver.create()
        new_booking = booking_service.create_booking(self.car, driver)
        self.assertEqual(new_booking.driver, driver)
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.get_state(), models.Booking.PENDING)

        # check we sent the right email - one email to the street team
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'Base letter request for {}'.format(new_booking.driver.full_name())
        )
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
        self.assertEqual(
            outbox[0].subject,
            'Your {} was successfully reserved'.format(new_booking.car.display_name()),
        )

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

    def test_checkout_before_other_checks_out(self):
        # set up the other driver, and create a booking for them
        other_driver = factories.CompletedDriver.create()
        other_booking = factories.Booking.create(car=self.car, driver=other_driver)

        new_booking = self._checkout_approved_driver()

        other_booking.refresh_from_db()
        self.assertEqual(other_booking.get_state(), models.Booking.INCOMPLETE)
        self.assertEqual(other_booking.incomplete_reason, models.Booking.REASON_ANOTHER_BOOKED_CC)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 3)

        # an email to the other driver to know their car is no longer available
        self.assertEqual(outbox[0].merge_vars.keys()[0], other_driver.email())
        self.assertEqual(
            outbox[0].subject,
            'Someone else rented your {}.'.format(other_booking.car.display_name())
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

    def test_checkout_before_other_uploads_docs(self):
        # set up the other driver, and create a booking for them
        other_driver = factories.Driver.create()
        other_booking = factories.Booking.create(car=self.car, driver=other_driver)

        new_booking = self._checkout_approved_driver()

        other_booking.refresh_from_db()
        self.assertEqual(other_booking.get_state(), models.Booking.INCOMPLETE)
        self.assertEqual(other_booking.incomplete_reason, models.Booking.REASON_ANOTHER_BOOKED_DOCS)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 3)

        # an email to the other driver to know their car is no longer available
        self.assertEqual(outbox[0].merge_vars.keys()[0], other_driver.email())
        self.assertEqual(
            outbox[0].subject,
            'Someone else rented your {}.'.format(other_booking.car.display_name())
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

        # a pickup confirmation to driver
        self.assertEqual(
            outbox[0].subject,
            'You are ready to drive!'
        )

        # a pickup confirmation to owner
        self.assertEqual(
            outbox[1].subject,
            '{} has paid you for the {}'.format(new_booking.driver.full_name(), new_booking.car.display_name()),
        )


    def test_pickup_six_sevenths_bug(self):
        self.car.min_lease = '_02_one_week'
        self.car.save()

        driver = factories.PaymentMethodDriver.create()
        new_booking = factories.AcceptedBooking.create(
            car=self.car,
            driver=driver,
        )

        # simulate using the app to set the end time to the min rental period
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        new_booking.end_time = today + timezone.timedelta(days=new_booking.car.minimum_rental_days())
        new_booking = booking_service.pickup(new_booking)

        self._check_payments_after_pickup(new_booking)


    def test_pickup_after_failure(self):
        self.car.min_lease = '_02_one_week'
        self.car.save()
        driver = factories.PaymentMethodDriver.create()

        new_booking = factories.AcceptedBooking.create(car=self.car, driver=driver, end_time=None)
        self.assertEqual(new_booking.get_state(), models.Booking.ACCEPTED)
        self.assertEqual(len(new_booking.payment_set.all()), 1)
        self.assertEqual(new_booking.payment_set.first().status, models.Payment.PRE_AUTHORIZED)

        # fail to pick up the car
        next_response = (models.Payment.DECLINED, 'This transaction was declined for some reason.',)
        gateway = payment_gateways.get_gateway('fake').next_payment_response.append(next_response)
        with self.assertRaises(booking_service.BookingError):
            new_booking = booking_service.pickup(new_booking)
        new_booking.refresh_from_db()  # make sure our local copy is fresh. pickup() changed it.

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'Payment {} for a {} failed.'.format(new_booking.payment_set.last(), new_booking.car)
        )

        # make sure there's a declined payment in there
        self.assertTrue(models.Payment.DECLINED in [p.status for p in new_booking.payment_set.all()])

        # successfully pick up the car
        new_booking = booking_service.pickup(new_booking)
        self._check_payments_after_pickup(new_booking)


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
        new_booking = booking_service.checkout(new_booking)
        booking_service.cancel(new_booking)

        # make sure the pre-authorized payment got voided
        self.assertEqual(len(new_booking.payment_set.all()), 1)
        self.assertEqual(new_booking.payment_set.last().status, models.Payment.VOIDED)

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
