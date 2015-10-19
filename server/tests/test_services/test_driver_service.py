# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from braintree.test.nonces import Nonces

from django.utils import timezone
from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ValidationError

from server.services import driver as driver_service
from server.services import booking as booking_service
from server import factories
from server.models import Booking

from owner_crm.tests import sample_merge_vars


class DriverServiceTest(TestCase):
    def setUp(self):
        self.driver = factories.Driver.create()
        self.car = factories.Car.create()


    def _set_all_docs(self):
        for doc in driver_service.doc_fields_and_names.keys():
            setattr(self.driver, doc, 'http://whatever.com')
        self.driver.save()

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


    def test_docs_uploaded_no_booking(self):
        self._set_all_docs()

        # we should have sent an email about the completed docs to ops
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'Uploaded documents from {}'.format(self.driver.phone_number())
        )
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(
            outbox[0].merge_vars[settings.OPS_EMAIL]['CTA_URL'].split('/')[-2],
            unicode(self.driver.pk),
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))


    def test_docs_uploaded_with_pending_booking(self):
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertEqual(new_booking.get_state(), Booking.PENDING)

        self._set_all_docs()
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        # we should have sent ops an email telling them about the new booking
        self._validate_new_booking_email(outbox[0], new_booking)

        # an email to ops to let them know when the documents were all uploaded
        self.assertEqual(outbox[1].merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(
            outbox[1].subject,
            'Uploaded documents from {}'.format(self.driver.phone_number())
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))


    def test_docs_approved_no_booking(self):
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


    def test_docs_approved_pending_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = factories.Booking.create(car=self.car, driver=self.driver)
        self.driver.documentation_approved = True
        self.driver.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        # and an email to the street team to get the base letter
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.STREET_TEAM_EMAIL)
        self.assertEqual(
            outbox[0].subject,
            "Base letter request for {}".format(new_booking.driver.full_name())
        )


    def test_docs_approved_reserved_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = factories.ReservedBooking.create(car=self.car, driver=self.driver)
        self.driver.documentation_approved = True
        self.driver.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        # and an email to the street team to get the base letter
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.STREET_TEAM_EMAIL)
        self.assertEqual(
            outbox[0].subject,
            "Base letter request for {}".format(new_booking.driver.full_name())
        )


    def test_docs_approved_return_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = factories.ReturnedBooking.create(car=self.car, driver=self.driver)
        self.driver.documentation_approved = True
        self.driver.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        self.assertEqual(outbox[0].merge_vars.keys()[0], self.driver.email())
        self.assertEqual(
            outbox[0].subject,
            'Welcome to idlecars, {}!'.format(self.driver.full_name())
        )


    def test_docs_approved_incomplete_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = factories.IncompleteBooking.create(car=self.car, driver=self.driver)
        self.driver.documentation_approved = True
        self.driver.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        self.assertEqual(outbox[0].merge_vars.keys()[0], self.driver.email())
        self.assertEqual(
            outbox[0].subject,
            'Welcome to idlecars, {}!'.format(self.driver.full_name())
        )


    def test_docs_approved_with_base_letter(self):
        self.driver = factories.CompletedDriver.create()
        self.driver.base_letter = 'some base letter'
        self.driver.save()

        new_booking = factories.ReservedBooking.create(car=self.car, driver=self.driver)
        self.driver.documentation_approved = True
        self.driver.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0)


    def test_base_letter_approved_pending_booking(self):
        self.driver = factories.ApprovedDriver.create()
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertEqual(new_booking.get_state(), Booking.PENDING)

        new_booking.driver.base_letter = 'some base letter'
        new_booking.driver.clean()
        new_booking.driver.save()

        # still in the PENDING state because they never checked out
        self.assertEqual(new_booking.get_state(), Booking.PENDING)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 3)

        # we should have sent an email to ops telling them about the new booking
        self._validate_new_booking_email(outbox[0], new_booking)

        # and an email to the street team to get the base letter
        self.assertEqual(outbox[1].merge_vars.keys()[0], settings.STREET_TEAM_EMAIL)
        self.assertEqual(
            outbox[1].subject,
            "Base letter request for {}".format(new_booking.driver.full_name())
        )

        # and an email to the driver telling them their docs and base letter were approved
        self.assertEqual(outbox[2].merge_vars.keys()[0], new_booking.driver.email())
        self.assertEqual(
            outbox[2].subject,
            "Your {} is waiting on your payment information!".format(new_booking.car.display_name())
        )


    def test_base_letter_approved_reserved_booking(self):
        self.driver = factories.ApprovedDriver.create()
        new_booking = factories.ReservedBooking.create(driver=self.driver)
        self.assertEqual(new_booking.get_state(), Booking.RESERVED)
        self.assertFalse(self.driver.base_letter_rejected)
        self.assertEqual(self.driver.base_letter, '')

        # THEN the documents are approved
        new_booking.driver.base_letter = 'some base letter'
        new_booking.driver.clean()
        new_booking.driver.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        # we should have sent an email to the owner asking them to add the driver to the insurance
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


    def test_base_letter_rejected(self):
        pass
