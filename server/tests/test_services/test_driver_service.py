# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from braintree.test.nonces import Nonces

from django.utils import timezone
from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ValidationError

from credit import factories as credit_factories
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

    def test_on_set_email(self):
        driver_service.on_set_email(self.driver)

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].subject, 'Welcome to All Taxi')

    def _set_all_docs(self):
        for doc in driver_service.doc_fields_and_names.keys():
            setattr(self.driver, doc, 'http://whatever.com')
        self.driver.save()

    def test_docs_uploaded_no_booking(self):
        self._set_all_docs()

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        # we should have sent a "welcome" email to the driver
        self.assertEqual(
            outbox[0].subject,
            'Welcome to All Taxi',
        )

        # ...and an informative email to ops
        self.assertEqual(
            outbox[1].subject,
            'Uploaded documents from {}'.format(self.driver.phone_number())
        )

        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_docs_uploaded_with_pending_booking(self):
        new_booking = booking_service.create_booking(self.car, self.driver)
        self.assertEqual(new_booking.get_state(), Booking.PENDING)

        self._set_all_docs()

        # we sent one informational email to ops
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 3)

    # def test_redeem_credit(self):
    #     code = credit_factories.CreditCode.create(credit_amount=50)
    #     driver_service.redeem_code(self.driver, code.credit_code)

    #     from django.core.mail import outbox
    #     self.assertEqual(len(outbox), 1)
    #     self.assertEqual(
    #         outbox[0].subject,
    #         'You have ${} credit in your All Taxi account'.format(self.driver.app_credit())
    #     )
