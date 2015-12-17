# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from idlecars.factories import AuthUser
from experiments.models import Experiment, Alternative, clear_caches
from experiments import experiments
from credit import credit_service
from server import factories
from server.services import driver as driver_service


class ExperimentServiceReferralTest(TestCase):
    def setUp(self):
        self.driver = factories.Driver.create()
        self.experiment = Experiment.objects.create(
            identifier='referral_rewards',
            start_time=timezone.now(),
            end_time=None,
        )

    def _set_all_docs(self):
        for doc in driver_service.doc_fields_and_names.keys():
            setattr(self.driver, doc, 'http://whatever.com')
        self.driver.save()

    def test_get_referral_rewards(self):
        default = Alternative.objects.create(
            experiment=self.experiment,
            identifier='default',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        Alternative.objects.create(
            experiment=self.experiment,
            identifier='50_50',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        self.experiment.default = default
        self.experiment.save()

        self._set_all_docs()
        self.driver.documentation_approved = True
        self.driver.save()

        # driver should have a referral credit code with one of the two experimental values
        code = self.driver.auth_user.customer.invite_code
        default = code.invitor_credit_amount == Decimal('25.00') and code.credit_amount == Decimal('75.00')
        cohort2 = code.invitor_credit_amount == Decimal('50.00') and code.credit_amount == Decimal('50.00')
        self.assertTrue(default or cohort2)

    def test_get_referral_rewards_biased(self):
        default = Alternative.objects.create(
            experiment=self.experiment,
            identifier='default',
            ratio=0,
            participant_count=0,
            conversion_count=0,
        )
        Alternative.objects.create(
            experiment=self.experiment,
            identifier='50_50',
            ratio=100,
            participant_count=0,
            conversion_count=0,
        )
        self.experiment.default = default
        self.experiment.save()

        self._set_all_docs()
        self.driver.documentation_approved = True
        self.driver.save()

        code = self.driver.auth_user.customer.invite_code
        reward = Decimal('50.00')
        self.assertTrue(code.invitor_credit_amount == reward and code.credit_amount == reward)

    # def test_increment_conversion(self):
    #     self.alternative_A = Alternative.objects.create(
    #         experiment=self.experiment,
    #         identifier='alt_A',
    #         ratio=50,
    #         participant_count=0,
    #         conversion_count=0,
    #     )
    #     self.alternative_B = Alternative.objects.create(
    #         experiment=self.experiment,
    #         identifier='alt_B',
    #         ratio=50,
    #         participant_count=0,
    #         conversion_count=0,
    #     )
    #     self.experiment.default = self.alternative_A
    #     self.experiment.save()

    #     existing_user = AuthUser.create()
    #     code = credit_service.create_invite_code(
    #         '50.00',
    #         '50.00',
    #         existing_user.customer,
    #     )

    #     # new driver comes along, redeems code and spends some cash
    #     driver = factories.ApprovedDriver.create()
    #     driver.auth_user.customer.invitor_code = code
    #     driver.auth_user.customer.save()

    #     driver_service.on_newly_converted(driver)

    #     # the experiment should show that this driver referred someone
    #     alt_id = experiments.assign_alternative(existing_user.username, self.experiment.identifier)
    #     alt = Alternative.objects.get(identifier=alt_id)
    #     self.assertEqual(alt.conversion_count, 1)

    # def test_not_increment_conversion_if_already_converted(self):
    #     self.alternative_A = Alternative.objects.create(
    #         experiment=self.experiment,
    #         identifier='alt_A',
    #         ratio=50,
    #         participant_count=0,
    #         conversion_count=0,
    #     )
    #     self.alternative_B = Alternative.objects.create(
    #         experiment=self.experiment,
    #         identifier='alt_B',
    #         ratio=50,
    #         participant_count=0,
    #         conversion_count=0,
    #     )
    #     self.experiment.default = self.alternative_A
    #     self.experiment.save()

    #     existing_user = AuthUser.create()
    #     code = credit_service.create_invite_code(
    #         '50.00',
    #         '50.00',
    #         existing_user.customer,
    #     )

    #     # new driver comes along, redeems code and spends some cash
    #     driver = factories.ApprovedDriver.create()
    #     driver.auth_user.customer.invitor_code = code
    #     driver.auth_user.customer.save()

    #     driver_service.on_newly_converted(driver)

    #     # ANOTHER new driver comes along, redeems THE SAME code and spends some cash
    #     driver2 = factories.ApprovedDriver.create()
    #     driver2.auth_user.customer.invitor_code = code
    #     driver2.auth_user.customer.save()

    #     driver_service.on_newly_converted(driver2)

    #     # the experiment should show that this driver referred someone
    #     alt_id = experiments.assign_alternative(existing_user.username, self.experiment.identifier)
    #     alt = Alternative.objects.get(identifier=alt_id)
    #     self.assertEqual(alt.conversion_count, 1)


class ExperimentServiceCouponTest(TestCase):
    def setUp(self):
        self.driver = factories.Driver.create()
        self.experiment = Experiment.objects.create(
            identifier='inactive_credit',
            start_time=timezone.now(),
            end_time=None,
        )

    def test_get_inactive_credit(self):
        default = Alternative.objects.create(
            experiment=self.experiment,
            identifier='default',
            ratio=40,
            participant_count=0,
            conversion_count=0,
        )
        Alternative.objects.create(
            experiment=self.experiment,
            identifier='coupon_100',
            ratio=40,
            participant_count=0,
            conversion_count=0,
        )
        Alternative.objects.create(
            experiment=self.experiment,
            identifier='coupon_150',
            ratio=20,
            participant_count=0,
            conversion_count=0,
        )
        self.experiment.default = default
        self.experiment.save()

        credit = driver_service.assign_inactive_credit(self.driver)
        self.assertTrue(credit in ['50.00', '100.00', '150.00'])

    def test_get_inactive_credit_biased(self):
        default = Alternative.objects.create(
            experiment=self.experiment,
            identifier='default',
            ratio=0,
            participant_count=0,
            conversion_count=0,
        )
        Alternative.objects.create(
            experiment=self.experiment,
            identifier='coupon_100',
            ratio=0,
            participant_count=0,
            conversion_count=0,
        )
        Alternative.objects.create(
            experiment=self.experiment,
            identifier='coupon_150',
            ratio=100,
            participant_count=0,
            conversion_count=0,
        )
        self.experiment.default = default
        self.experiment.save()

        credit = driver_service.assign_inactive_credit(self.driver)
        self.assertTrue(credit == '150.00')
