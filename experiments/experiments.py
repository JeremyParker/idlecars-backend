# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import bisect
import hashlib

from django.utils import timezone

import models


def assign_alternative(identity, experiment_id):
    """Start an experiment by returning an alternative identifier assigned to identity.

    Note, that a generic alternative identifier 'default' will be
    returned in certain circumstances, like:
    - if `experiment_id` is not found;
    - if experiment has no alternatives;
    - if experiment has no default set.

    Therefore, it is a good idea to explicitly create one alternative
    named 'default', when setting up a new experiment.

    Arguments:
    - identity: an arbitrary string, identifying a test subject (e.g. customer, device).
    - experiment_id: string, identifier of experiment to conduct.

    Returns: string, identifier of one of the alternatives associated
    with experiment.
    """
    assert isinstance(identity, basestring)
    assert isinstance(experiment_id, basestring)

    try:
        experiment = models.Experiment.objects.get_experiment(experiment_id)
    except (models.Experiment.DoesNotExist, KeyError):
        return 'default'

    now = timezone.now()
    if experiment.start_time and experiment.start_time > now:
        if experiment.default:
            return experiment.default.identifier
        else:
            return 'default'
    if experiment.end_time and experiment.end_time < now:
        if experiment.winner:
            return experiment.winner.identifier
        else:
            return experiment.default.identifier

    hasher = hashlib.md5()
    hasher.update(experiment_id + identity)
    # the [-12:] bit is to keep the value inside float precision.
    value = int(hasher.hexdigest()[-12:], 16) % experiment.boundaries[-1]
    index = bisect.bisect_right(experiment.boundaries, value)
    if not experiment.alternatives:
        alternative_id = 'default'
    else:
        alternative_id = experiment.alternatives[index].identifier

    return alternative_id


def get_assignments(identity):
    """Return a dictionary with identity alternative assignment information.

    Arguments:
    - identity: string, identifying a test subject (e.g. customer, device)
    """
    assert isinstance(identity, basestring)

    now = timezone.now()
    experiments = models.Experiment.objects.get_experiments()

    assignments = {}
    for experiment_id, experiment in experiments.iteritems():
        if experiment.start_time < now:
            assignments[experiment_id] = assign_alternative(identity, experiment_id)

    return assignments
