# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

from django.utils import timezone

from experiments import experiments, models
from experiments.testutils import TestCase


class AssignAlternativeTest(TestCase):

    def setUp(self):
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

    def test_assign_alternative_alternative_assignment(self):
        self.assertEquals(
            experiments.assign_alternative(
                self.identity_A,
                self.experiment.identifier,
            ),
            self.alternative_B.identifier,
        )

        self.assertEquals(
            experiments.assign_alternative(
                self.identity_A,
                self.experiment.identifier
            ),
            self.alternative_B.identifier,
        )

        self.assertEquals(
            experiments.assign_alternative(
                self.identity_B,
                self.experiment.identifier
            ),
            self.alternative_A.identifier,
        )

        self.assertEquals(
            experiments.assign_alternative(
                self.identity_B,
                self.experiment.identifier
            ),
            self.alternative_A.identifier,
        )

    def test_assign_alternative_not_started(self):
        self.experiment.start_time = timezone.now() + timedelta(hours=1)
        self.experiment.save()

        if hasattr(models.Alternative.objects, '_alternatives'):
            del(models.Alternative.objects._alternatives)
        if hasattr(models.Experiment.objects, '_experiments'):
            del(models.Experiment.objects._experiments)

        self.assertEquals(
            experiments.assign_alternative(
                self.identity_A,
                self.experiment.identifier
            ),
            self.alternative_A.identifier,
        )

        self.assertEquals(
            experiments.assign_alternative(
                self.identity_B,
                self.experiment.identifier
            ),
            self.alternative_A.identifier,
        )

        self.assertEquals(
            self.experiment.default.identifier,
            self.alternative_A.identifier,
        )

    def test_assign_alternative_ended_no_winner(self):
        self.experiment.start_time = timezone.now() - timedelta(hours=2)
        self.experiment.end_time = timezone.now() - timedelta(hours=1)
        self.experiment.save()

        self.assertEquals(
            experiments.assign_alternative(
                self.identity_A,
                self.experiment.identifier
            ),
            self.alternative_A.identifier,
        )

        self.assertEquals(
            experiments.assign_alternative(
                self.identity_B,
                self.experiment.identifier
            ),
            self.alternative_A.identifier,
        )

    def test_assign_alternative_ended_with_winner(self):
        self.experiment.start_time = timezone.now() - timedelta(hours=2)
        self.experiment.end_time = timezone.now() - timedelta(hours=1)
        self.experiment.save()

        self.experiment.winner = self.alternative_B
        self.experiment.save()

        self.assertEquals(
            experiments.assign_alternative(
                self.identity_A,
                self.experiment.identifier
            ),
            self.alternative_B.identifier,
        )

        self.assertEquals(
            experiments.assign_alternative(
                self.identity_B,
                self.experiment.identifier
            ),
            self.alternative_B.identifier,
        )

    def test_assign_alternative_invalid_arguments(self):
        with self.assertRaises(Exception):
            experiments.assign_alternative(1, 'test')
        with self.assertRaises(Exception):
            experiments.assign_alternative('test', 1)
        with self.assertRaises(Exception):
            experiments.assign_alternative(1, 1)


class GetAssignmentsTest(TestCase):

    def setUp(self):
        self.experiment = models.Experiment.objects.create(
            identifier='test_experiment',
            start_time=timezone.now() - timedelta(hours=1),
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

        self.identity = 'identity_1'

    def test_get_assignments_none(self):
        self.assertDictEqual(
            experiments.get_assignments(self.identity),
            {self.experiment.identifier: self.alternative_B.identifier}
        )

    def test_get_assignments_one(self):
        alternative_id = experiments.assign_alternative(self.identity, self.experiment.identifier)
        self.assertIsNotNone(alternative_id)
        self.assertDictEqual(
            experiments.get_assignments(self.identity),
            {self.experiment.identifier: alternative_id}
        )

    def test_get_assignments_two(self):
        experiment = models.Experiment.objects.create(
            identifier='test_experiment2',
            start_time=timezone.now() - timedelta(hours=1),
            end_time=None,
        )
        alternative_A = models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_A',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_B',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        experiment.default = alternative_A
        experiment.save()

        alternative_id_one = experiments.assign_alternative(self.identity, self.experiment.identifier)
        self.assertIsNotNone(alternative_id_one)
        alternative_id_two = experiments.assign_alternative(self.identity, experiment.identifier)
        self.assertIsNotNone(alternative_id_two)
        self.assertDictEqual(
            experiments.get_assignments(self.identity),
            {self.experiment.identifier: alternative_id_one,
             experiment.identifier: alternative_id_two}
        )

    def test_get_assignments_one_not_started(self):
        experiment = models.Experiment.objects.create(
            identifier='test_experiment2',
            start_time=timezone.now() + timedelta(hours=1),
            end_time=None,
        )
        alternative_A = models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_A2',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_B2',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        experiment.default = alternative_A
        experiment.save()

        alternative_id = experiments.assign_alternative(self.identity, self.experiment.identifier)
        self.assertIsNotNone(alternative_id)
        self.assertDictEqual(
            experiments.get_assignments(self.identity),
            {self.experiment.identifier: alternative_id}
        )

    def test_get_assignments_one_ended_no_winner(self):
        experiment = models.Experiment.objects.create(
            identifier='test_experiment2',
            start_time=timezone.now() - timedelta(hours=2),
            end_time=timezone.now() - timedelta(hours=1),
        )
        alternative_A = models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_A2',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_B2',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        experiment.default = alternative_A
        experiment.save()

        alternative_id_active = experiments.assign_alternative(self.identity, self.experiment.identifier)
        self.assertIsNotNone(alternative_id_active)
        alternative_id_ended = experiments.assign_alternative(self.identity, experiment.identifier)
        self.assertEquals(alternative_id_ended, experiment.default.identifier)
        self.assertDictEqual(
            experiments.get_assignments(self.identity),
            {self.experiment.identifier: alternative_id_active,
             experiment.identifier: experiment.default.identifier}
        )

    def test_get_assignments_one_ended_with_winner(self):
        experiment = models.Experiment.objects.create(
            identifier='test_experiment2',
            start_time=timezone.now() - timedelta(hours=2),
            end_time=timezone.now() - timedelta(hours=1),
        )
        alternative_A = models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_A2',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        alternative_B = models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_B2',
            ratio=50,
            participant_count=0,
            conversion_count=0,
        )
        experiment.default = alternative_A
        experiment.winner = alternative_B
        experiment.save()

        alternative_id_active = experiments.assign_alternative(self.identity, self.experiment.identifier)
        self.assertIsNotNone(alternative_id_active)
        alternative_id_ended = experiments.assign_alternative(self.identity, experiment.identifier)
        self.assertEquals(alternative_id_ended, experiment.winner.identifier)
        self.assertDictEqual(
            experiments.get_assignments(self.identity),
            {self.experiment.identifier: alternative_id_active,
             experiment.identifier: experiment.winner.identifier}
        )
