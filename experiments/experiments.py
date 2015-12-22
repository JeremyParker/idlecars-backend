# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import bisect
import hashlib

from django.utils import timezone
from django.db.models import F

import models


def assign_alternative(identity, experiment_id):
    """Start an experiment by returning an alternative identifier assigned to identity.
    This method can be called multiple times to get the assigment for an identity.

    Note, that a generic alternative identifier 'default' will be
    returned in certain circumstances, like:
    - if `experiment_id` is not found;
    - if experiment has no alternatives;
    - if experiment has no default set.

    Therefore, it is a good idea to explicitly create one alternative
    named 'default', when setting up a new experiment.

    Arguments:
    - identity: an arbitrary string, identifying a test subject (e.g. customer, session).
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

    assignment, new = models.Assignment.objects.get_or_create(
        experiment=experiment,
        identity=identity,
    )
    if new:
        alternative = calculate_alternative(identity, experiment)
        if alternative:
            assignment.alternative = alternative
        assignment.save()

    if not assignment.alternative:
        return 'default'
    else:
        return assignment.alternative.identifier


def calculate_alternative(identity, experiment):
    now = timezone.now()
    if experiment.start_time and experiment.start_time > now:
        if experiment.default:
            return experiment.default
        else:
            return None
    if experiment.end_time and experiment.end_time < now:
        if experiment.winner:
            return experiment.winner
        else:
            return experiment.default

    if not experiment.alternatives:
        return None

    hasher = hashlib.md5()
    hasher.update(experiment.identifier + identity)
    # the [-12:] bit is to keep the value inside float precision.
    value = int(hasher.hexdigest()[-12:], 16) % experiment.boundaries[-1]
    index = bisect.bisect_right(experiment.boundaries, value)
    return experiment.alternatives[index]


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
        if experiment.start_time and experiment.start_time < now:
            assignments[experiment_id] = assign_alternative(identity, experiment_id)

    return assignments


def increment_conversion(identity, experiment_id):
    try:
        assignment = models.Assignment.objects.get(
            experiment__identifier=experiment_id,
            identity=identity,
            converted_time__isnull=True,
        )
    except (models.Assignment.DoesNotExist):
        # if this identity wasn't assigned to an alternative, we don't track their conversions.
        return

    assignment.converted_time = timezone.now()
    assignment.save()
