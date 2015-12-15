# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from experiments.models import Experiment, Alternative, clear_caches
from server import factories
from server.services import driver as driver_service


class ExperimentServiceTest(TestCase):
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

        # driver should have a referral credit code with one of the two experimental values
        code = self.driver.auth_user.customer.invite_code
        reward = Decimal('50.00')
        self.assertTrue(code.invitor_credit_amount == reward and code.credit_amount == reward)
