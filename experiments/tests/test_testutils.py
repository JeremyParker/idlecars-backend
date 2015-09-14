# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from experiments import experiments
from experiments.testutils import experiment_list


class ExperimentContextManagerTest(TestCase):

    @experiment_list(testutils='decorator')
    def test_function_decorator(self):
        self.assertEquals(experiments.assign_alternative('blabla', 'testutils'), 'decorator')

    def test_context_manager(self):
        with experiment_list(testutils='context_manager'):
            self.assertEquals(experiments.assign_alternative('blabla', 'testutils'), 'context_manager')

    def test_failure(self):
        with experiment_list(testutils='context_manager'):
            self.assertEquals(experiments.assign_alternative('blabla', 'testutils'), 'context_manager')
        self.assertEquals(experiments.assign_alternative('blabla', 'testutils'), 'default')
