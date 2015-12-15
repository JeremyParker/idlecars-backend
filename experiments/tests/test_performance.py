# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache
from django.utils import timezone

from experiments import models, experiments
from experiments.testutils import TestCase


class AssignAlternativeTest(TestCase):

    def setUp(self):
        self.experiment = models.Experiment.objects.create(
            identifier='test_performance',
            start_time=timezone.now(),
            end_time=None,
        )
        self.alternative_A = models.Alternative.objects.create(
            experiment=self.experiment,
            identifier='alternative_A',
            participant_count=0,
            conversion_count=0,
            ratio=50,
        )
        self.alternative_B = models.Alternative.objects.create(
            experiment=self.experiment,
            identifier='alternative_B',
            participant_count=0,
            conversion_count=0,
            ratio=50,
        )
        self.experiment.default = self.alternative_B
        self.experiment.save()

        cache.clear()

    def test_assign_alternative_nonexistant(self):
        with self.assertNumQueries(1):
            self.assertEquals(experiments.assign_alternative('uuid', 'nonexistant'), 'default')

        with self.assertNumQueries(0):
            self.assertEquals(experiments.assign_alternative('uuid', 'nonexistant'), 'default')

    def test_assign_alternative_success(self):
        with self.assertNumQueries(2):
            alternative_id1 = experiments.assign_alternative('uuid', self.experiment.identifier)

        with self.assertNumQueries(0):
            alternative_id2 = experiments.assign_alternative('uuid', self.experiment.identifier)

        self.assertEquals(alternative_id1, alternative_id2)
