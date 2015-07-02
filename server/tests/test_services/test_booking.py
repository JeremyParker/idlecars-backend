# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from collections import OrderedDict

from django.utils import timezone
from django.test import TestCase

from server.services import booking as booking_service
from server import factories, models

from crm.tests import sample_merge_vars


class BookingServiceTest(TestCase):
    def setUp(self):
        owner = factories.Owner.create(state_code='NY',)
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
        self.assertEqual(
            outbox[0].merge_vars['support@idlecars.com']['CTA_URL'].split('/')[-2],
            unicode(new_booking.pk),
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))


    def test_create_booking_docs_complete(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertIsNotNone(new_booking)
        self.assertEqual(new_booking.driver, self.driver)
        self.assertEqual(new_booking.car, self.car)
        self.assertEqual(new_booking.state, models.Booking.COMPLETE)

        # we should have sent an email to ops telling them about the new booking
        from django.core.mail import outbox
        self.assertEqual(
            outbox[0].subject,
            'New Booking from {}'.format(self.driver.phone_number())
        )
        self.assertEqual(
            outbox[0].merge_vars['support@idlecars.com']['CTA_URL'].split('/')[-2],
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
        self.assertEqual(outbox[0].subject, 'A driver has booked your {}.'.format(new_booking.car.__unicode__()))
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))
