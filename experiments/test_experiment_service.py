# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.utils import timezone

from experiments import experiments, models
from experiments.testutils import TestCase
from server import factories, services

class CreditCodeBackfillTest(TestCase):
    def test_increment_conversion(self):
        self.identity_A = '1dd26432-25f3-468f-83eb-e1261bf29fa0'
        self.identity_B = '27b72751-3b35-4d03-aa13-cf623514bb3a'
        self.experiment = models.Experiment.objects.create(
            identifier='test_experiment',
            start_time=timezone.now(),
            end_time=None,
        )
        self.alternative_A = models.Alternative.objects.create(
            experiment=self.experiment,
            identifier='alt_A',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        self.alternative_B = models.Alternative.objects.create(
            experiment=self.experiment,
            identifier='alt_B',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        self.experiment.default = self.alternative_A
        self.experiment.save()

        existing_user = AuthUser.create()
        code = credit_service.create_invite_code(
            '50.00',
            '50.00',
            existing_user.customer,
        )

        # new driver comes along, redeems code and spends some cash
        driver = factories.Driver.create()
        services.driver.on_newly_converted(driver)

        # the experiment should show that this driver referred someone
        alt_id = experiments.assign_alternative(existing_user.customer, self.experiment.identifier)
        alt = models.Alternative.objects.get(identifier=alt_id)
        self.assertEqual(alt.conversion_count, 1)
