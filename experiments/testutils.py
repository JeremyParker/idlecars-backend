# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import functools
import types

from django import test

import experiments
import models


class ExperimentContextManager(object):
    """Allows temporarily 'mocking' out experiments.

    Useful for testing.

    >> @experiments(dummy='alternative_A')
    >> def foo():
    >>     print experiments.assign_alternative('identity', 'dummy')

    >> def foo():
    >>     with experiments(dummy='alternative_A'):
    >>         print experiments.assign_alternative('identity', 'dummy')
    """
    def __init__(self, **experiment_list):
        self.experiments = experiments
        self.experiment_list = experiment_list

    def __call__(self, func_or_class):
        if isinstance(func_or_class, (types.FunctionType, types.MethodType)):
            # function/method decorator
            func = func_or_class

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self:
                    return func(*args, **kwargs)

            return wrapper
        elif isinstance(func_or_class, (types.TypeType, types.ClassType)) and hasattr(func_or_class, 'run'):
            # unittest class decorator
            klass = func_or_class
            run = klass.run

            @functools.wraps(run)
            def wrapper(*args, **kwargs):
                with self:
                    return run(*args, **kwargs)

            klass.run = wrapper
            return klass
        else:
            raise ValueError("Can only work with functions or unittest classes")

    def __enter__(self):
        self.assign_alternative_func = experiments.assign_alternative

        def wrapper(identity, experiment_id):
            if experiment_id in self.experiment_list:
                return self.experiment_list[experiment_id]
            return self.assign_alternative_func(identity, experiment_id)

        self.experiments.assign_alternative = wrapper

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.experiments.assign_alternative = self.assign_alternative_func


experiment_list = ExperimentContextManager


class TestCase(test.TestCase):

    def tearDown(self):
        if hasattr(models.Alternative.objects, '_alternatives'):
            del(models.Alternative.objects._alternatives)
        if hasattr(models.Experiment.objects, '_experiments'):
            del(models.Experiment.objects._experiments)
