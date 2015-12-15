# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache
from django.utils import timezone

from experiments import models
from experiments.testutils import TestCase


class ExperimentTest(TestCase):

    def setUp(self):
        self.experiment = models.Experiment.objects.create(
            identifier='test_models',
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

    def test_alternatives(self):
        expected = [
            self.alternative_A,
            self.alternative_B,
        ]

        for idx, alternative in enumerate(self.experiment.alternatives):
            self.assertEquals(
                alternative.pk,
                expected[idx].pk,
            )

    def test_boundaries(self):
        self.assertListEqual(self.experiment.boundaries, [50, 100])

        self.alternative_A.ratio = 30
        self.alternative_A.save()
        self.alternative_B.ratio = 30
        self.alternative_B.save()

        alternative_C = models.Alternative.objects.create(
            experiment=self.experiment,
            identifier='alternative_C',
            participant_count=0,
            conversion_count=0,
            ratio=40,
        )

        if hasattr(models.Alternative.objects, '_alternatives'):
            del(models.Alternative.objects._alternatives)

        self.assertListEqual(self.experiment.boundaries, [30, 60, 100])

        alternative_C.ratio = 10
        alternative_C.save()

        models.Alternative.objects.create(
            experiment=self.experiment,
            identifier='alternative_D',
            participant_count=0,
            conversion_count=0,
            ratio=30
        )

        if hasattr(models.Alternative.objects, '_alternatives'):
            del(models.Alternative.objects._alternatives)

        self.assertListEqual(self.experiment.boundaries, [30, 60, 70, 100])
