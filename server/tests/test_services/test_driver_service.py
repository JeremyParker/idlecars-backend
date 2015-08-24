# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from braintree.test.nonces import Nonces

from django.utils import timezone
from django.test import TestCase
from django.conf import settings

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

    def test_documents_approved_pending_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertEqual(new_booking.get_state(), Booking.PENDING)

        new_booking.driver.documentation_approved = True
        new_booking.driver.save()

        # still in the PENDING state because they never checked out
        self.assertEqual(new_booking.get_state(), Booking.PENDING)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        # we should have sent an email to ops telling them about the new booking
        self._validate_new_booking_email(outbox[0], new_booking)

        # and an email to the driver telling them their docs were approved
        self.assertEqual(outbox[1].merge_vars.keys()[0], new_booking.driver.email())
        self.assertEqual(
            outbox[1].subject,
            "Welcome to idlecars, {}!".format(self.driver.full_name())
        )

    def test_documents_approved_reserved_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertEqual(new_booking.get_state(), Booking.PENDING)

        # booking is reserved with the deposit paid
        booking_service.checkout(new_booking, nonce=Nonces.Transactable)
        self.assertEqual(new_booking.get_state(), Booking.RESERVED)

        # THEN the documents are approved
        new_booking.driver.documentation_approved = True
        new_booking.driver.save()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        self._validate_new_booking_email(outbox[0], new_booking)

        # we should have sent an email to the owner asking them to add the driver to the insurance
        self.assertEqual(outbox[1].merge_vars.keys()[0], new_booking.car.owner.email())
        self.assertEqual(
            outbox[1].subject,
            'A driver has booked your {}.'.format(new_booking.car.__unicode__())
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))
