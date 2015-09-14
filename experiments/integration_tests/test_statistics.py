# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict
import random
import uuid

from django.utils import timezone

from experiments import experiments, models
from experiments.testutils import TestCase


class StatisticsTest(TestCase):

    def setUp(self):
        gen = random.Random(20140812)

        self.list_of_identities = [unicode(uuid.UUID(int=gen.getrandbits(128), version=4)) for i in xrange(10000)]

    def test_even_distribution(self):
        experiment = models.Experiment.objects.create(
            identifier='test_experiment',
            start_time=timezone.now(),
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

        participants = defaultdict(int)
        for identity in self.list_of_identities:
            alt = experiments.assign_alternative(identity, experiment.identifier)
            participants[alt] += 1

        self.assertEquals(
            sum(participants.values()),
            len(self.list_of_identities),
        )

        # NOTE(julius): our assignment algorithm can be viewed as a coin
        # that may or not be fair. If we toss it 10'000 times and it comes
        # up heads 5150 times, can we call it fair? [1]
        #
        # [1]: http://www.stanford.edu/class/psych252/tutorials/binomial_probability.html
        interval = (4835, 5165)
        self.assertTrue(interval[0] <= participants['alt_A'] <= interval[1])
        self.assertTrue(interval[0] <= participants['alt_B'] <= interval[1])

    def test_biased_distribution(self):
        experiment = models.Experiment.objects.create(
            identifier='test_biased',
            start_time=timezone.now(),
            end_time=None,
        )
        alternative_A = models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_A',
            ratio=70,
            participant_count=0,
            conversion_count=0,
        )
        models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_B',
            ratio=10,
            participant_count=0,
            conversion_count=0,
        )
        models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_C',
            ratio=10,
            participant_count=0,
            conversion_count=0,
        )
        models.Alternative.objects.create(
            experiment=experiment,
            identifier='alt_D',
            ratio=10,
            participant_count=0,
            conversion_count=0,
        )
        experiment.default = alternative_A
        experiment.save()

        participants = defaultdict(int)
        for identity in self.list_of_identities:
            alt = experiments.assign_alternative(identity, experiment.identifier)
            participants[alt] += 1

        interval = (6849, 7150)
        self.assertTrue(interval[0] <= participants['alt_A'] <= interval[1])

        interval = (903, 1100)
        self.assertTrue(interval[0] <= participants['alt_B'] <= interval[1])

        interval = (903, 1100)
        self.assertTrue(interval[0] <= participants['alt_C'] <= interval[1])

        interval = (903, 1100)
        self.assertTrue(interval[0] <= participants['alt_D'] <= interval[1])
