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
        user_account = factories.UserAccount.create(owner=owner)

        make_model = factories.MakeModel.create()
        self.car = factories.Car.create(
            owner=owner,
            make_model=make_model,
            status='available',
            next_available_date=timezone.now().date() + datetime.timedelta(days=1),
            min_lease='_03_two_weeks',
            hybrid=True,
        )
        self.driver = factories.Driver.create()

    def test_create_pending_booking(self):
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertIsNotNone(new_booking)
        self.assertEqual(new_booking.driver, self.driver)
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.state, models.Booking.PENDING)

        # we should have sent an email to ops telling them about the new booking
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'New Booking from {}'.format(self.driver.phone_number())
        )
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(
            outbox[0].merge_vars[settings.OPS_EMAIL]['CTA_URL'].split('/')[-2],
            unicode(new_booking.pk),
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))


    def test_create_booking_docs_complete(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertIsNotNone(new_booking)
        self.assertEqual(new_booking.driver, self.driver)
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.state, models.Booking.PENDING)

        # we should have sent an email to ops telling them about the new booking
        from django.core.mail import outbox
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(
            outbox[0].subject,
            'New Booking from {}'.format(self.driver.phone_number())
        )
        self.assertEqual(
            outbox[0].merge_vars[settings.OPS_EMAIL]['CTA_URL'].split('/')[-2],
            unicode(new_booking.pk),
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_create_booking_docs_approved(self):
        self.driver = factories.ApprovedDriver.create()
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertIsNotNone(new_booking)
        self.assertEqual(new_booking.driver, self.driver)
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.state, models.Booking.REQUESTED)

        # check we sent the right email
        from django.core.mail import outbox
        # TODO - driver_emails.new_booking_insurance_requested()

        self.assertEqual(len(outbox), 1)

        # an email to the owner to let them know their car got booked
        self.assertEqual(outbox[0].merge_vars.keys()[0], new_booking.car.owner.email())
        self.assertEqual(
            outbox[0].subject,
            'A driver has booked your {}.'.format(new_booking.car.__unicode__())
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_create_booking_with_others_too_slow(self):
        # set up the other driver, and create a booking for them
        self.other_driver = factories.Driver.create()
        booking_service.create_booking(self.car, self.other_driver)

        self.driver = factories.ApprovedDriver.create()
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertIsNotNone(new_booking)
        self.assertEqual(new_booking.driver, self.driver)
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.state, models.Booking.REQUESTED)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 3)

        # an email to support that there's a new booking
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(
            outbox[0].subject,
            'New Booking from {}'.format(self.other_driver.phone_number())
        )

        # an email to the owner to get the driver on insurance
        self.assertEqual(outbox[1].merge_vars.keys()[0], new_booking.car.owner.email())
        self.assertEqual(
            outbox[1].subject,
            'A driver has booked your {}.'.format(new_booking.car.__unicode__())
        )

        # an email to the other driver to know their car is no longer available
        self.assertEqual(outbox[2].merge_vars.keys()[0], self.other_driver.email())
        self.assertEqual(
            outbox[2].subject,
            'Someone else rented your {}.'.format(new_booking.car.__unicode__())
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_documents_uploaded(self):
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertEqual(new_booking.state, models.Booking.PENDING)

        # set all the document urls
        for doc in driver_service.doc_fields_and_names.keys():
            setattr(new_booking.driver, doc, "http://media.giphy.com/media/y8Mz1yj13s3kI/giphy.gif")
        new_booking.driver.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        # we should have sent an email to ops telling them about the new booking
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(
            outbox[0].subject,
            'New Booking from {}'.format(self.driver.phone_number())
        )

        # an email to ops to let them know when the documents were all uploaded
        self.assertEqual(outbox[1].merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(
            outbox[1].subject,
            'Uploaded documents from {}'.format(self.driver.phone_number())
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_documents_approved(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertEqual(new_booking.state, models.Booking.PENDING)

        new_booking.driver.documentation_approved = True
        new_booking.driver.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 3)

        # we should have sent an email to ops telling them about the new booking
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(
            outbox[0].subject,
            'New Booking from {}'.format(self.driver.phone_number())
        )

        # and an email to the driver telling them their docs were approved
        self.assertEqual(outbox[1].merge_vars.keys()[0], new_booking.driver.email())
        self.assertEqual(
            outbox[1].subject,
            "Your documents have been reviewed and approved"
        )

        # and an email to the owner asking them to add the driver to the insurance
        self.assertEqual(outbox[2].merge_vars.keys()[0], new_booking.car.owner.email())
        self.assertEqual(
            outbox[2].subject,
            'A driver has booked your {}.'.format(new_booking.car.__unicode__())
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_documents_approved_no_booking(self):
        self.driver = factories.CompletedDriver.create()
        self.driver.documentation_approved = True
        self.driver.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        self.assertEqual(outbox[0].merge_vars.keys()[0], self.driver.email())
        self.assertEqual(
            outbox[0].subject,
            'Welcome to idlecars, {}!'.format(self.driver.full_name())
        )

    def test_cancel_pending_booking(self):
        new_booking = booking_service.create_booking(self.car, self.driver)
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
        booking_service.cancel(new_booking)

        ''' we should have sent
        - message to the owner to send the insurance docs,
        - message to the owner to cancel the insurance request.
        - message to ops when the booking was canceled,
        - message to the driver to confirm the booking was canceled,
        '''
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 4)

    def test_correct_start_time(self):
        new_booking = booking_service.create_booking(self.car, self.driver)

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
