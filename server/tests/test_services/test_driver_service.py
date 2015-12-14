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


class DriverPaymentMethodTest(TestCase):
    def test_default_payment_method(self):
        self.driver = factories.Driver.create()
        legit = factories.PaymentMethod.create(driver=self.driver)
        rejected = factories.RejectedPaymentMethod.create(driver=self.driver)
        default = driver_service.get_default_payment_method(self.driver)
        self.assertEqual(default, legit)


class DriverServiceTest(TestCase):
    def setUp(self):
        self.driver = factories.Driver.create()
        self.car = factories.BookableCar.create()

    def _set_all_docs(self):
        for doc in driver_service.doc_fields_and_names.keys():
            setattr(self.driver, doc, 'http://whatever.com')
        self.driver.save()

    def _validate_base_letter_email(self, new_booking):
        self.driver.documentation_approved = True
        self.driver.save()

        # the driver should now have an invite code
        self.assertTrue(self.driver.auth_user.customer.invite_code)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        # and an email to the street team to get the base letter
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.STREET_TEAM_EMAIL)
        self.assertEqual(
            outbox[0].subject,
            "Base letter request for {}".format(new_booking.driver.full_name())
        )

    def _validate_no_booking_email(self):
        self.driver.documentation_approved = True
        self.driver.save()

        # the driver should now have an invite code
        self.assertTrue(self.driver.auth_user.customer.invite_code)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)

        self.assertEqual(outbox[0].merge_vars.keys()[0], self.driver.email())
        self.assertEqual(
            outbox[0].subject,
            'Welcome to idlecars, {}!'.format(self.driver.full_name())
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
        self.assertEqual(len(outbox), 1)

        # an email to ops to let them know when the documents were all uploaded
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.OPS_EMAIL)
        self.assertEqual(
            outbox[0].subject,
            'Uploaded documents from {}'.format(self.driver.phone_number())
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_docs_approved_no_booking(self):
        self.driver = factories.CompletedDriver.create()
        self._validate_no_booking_email()

    def test_docs_approved_pending_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = factories.Booking.create(car=self.car, driver=self.driver)

        self._validate_base_letter_email(new_booking)

    def test_docs_approved_reserved_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = factories.ReservedBooking.create(car=self.car, driver=self.driver)
        self._validate_base_letter_email(new_booking)

    def test_docs_approved_requested_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = factories.RequestedBooking.create(car=self.car, driver=self.driver)
        self._validate_base_letter_email(new_booking)

    def test_docs_approved_return_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = factories.ReturnedBooking.create(car=self.car, driver=self.driver)
        self._validate_base_letter_email(new_booking)

    def test_docs_approved_incomplete_booking(self):
        self.driver = factories.CompletedDriver.create()
        new_booking = factories.IncompleteBooking.create(car=self.car, driver=self.driver)
        self._validate_base_letter_email(new_booking)

    def test_docs_approved_with_base_letter(self):
        self.driver = factories.CompletedDriver.create()
        self.driver.base_letter = 'some base letter'
        self.driver.save()

        new_booking = factories.ReservedBooking.create(car=self.car, driver=self.driver)
        self.driver.documentation_approved = True
        self.driver.save()

        # the driver should now have an invite code
        self.assertTrue(self.driver.auth_user.customer.invite_code)

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
        self.assertEqual(len(outbox), 2)

        # and an email to the street team to get the base letter
        self.assertEqual(outbox[0].merge_vars.keys()[0], settings.STREET_TEAM_EMAIL)
        self.assertEqual(
            outbox[0].subject,
            "Base letter request for {}".format(new_booking.driver.full_name())
        )

        # and an email to the driver telling them their docs and base letter were approved
        self.assertEqual(outbox[1].merge_vars.keys()[0], new_booking.driver.email())
        self.assertEqual(
            outbox[1].subject,
            "Don't forget to reserve your {}!".format(new_booking.car.display_name())
        )

    def test_base_letter_approved_reserved_booking(self):
        self.driver = factories.ApprovedDriver.create()
        new_booking = factories.ReservedBooking.create(driver=self.driver)
        self.assertEqual(new_booking.get_state(), Booking.RESERVED)
        self.assertFalse(self.driver.base_letter_rejected)
        self.assertEqual(self.driver.base_letter, '')

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

    def test_redeem_credit(self):
        from credit import credit_service
        code = credit_service.create_invite_code('50.00')
        driver_service.redeem_code(self.driver, code.credit_code)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(
            outbox[0].subject,
            'You have ${} towards and Idlecars rental'.format(self.driver.app_credit())
        )
