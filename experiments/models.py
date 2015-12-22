# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict
from datetime import timedelta

from django.conf import settings
from django.core import exceptions
from django.core.cache import cache
from django.db import models
from django.utils import timezone


# Time in seconds how long local object cache should persist.
LOCAL_CACHE_LIFETIME = getattr(settings, 'EXPERIMENTS_LOCAL_CACHE_LIFETIME', 60)


class Model(models.Model):
    class Meta:
        abstract = True

    def delete(self):
        raise Exception(
            "Experiments or alternatives can not be deleted. You should end them instead."
        )


class ExperimentManager(models.Manager):
    def get_experiment(self, experiment_id):
        """Returns active experiments from cache or db.

        Return: `Experiment`
        """
        experiments = self.get_experiments()
        return experiments[experiment_id]

    def get_experiments(self):
        """Returns a dictionary with all active experiments from cache or db.

        Return: dictionary {experiment.identifier: experiment}
        """
        now = timezone.now()
        self._local_cache_last_update = getattr(self, '_local_cache_last_update', now)
        if now - self._local_cache_last_update > timedelta(seconds=LOCAL_CACHE_LIFETIME) or not hasattr(self, '_experiments'):
            experiments = cache.get('experiments_experiments')
            if not experiments:
                list_of_experiments = Experiment.objects.exclude(default=None)
                experiments = {exp.identifier: exp for exp in list_of_experiments}
                cache.set('experiments_experiments', experiments)
            self._experiments = experiments
            self._local_cache_last_update = now
        return self._experiments


class Experiment(Model):
    """Represents an A/B Test experiment.

    Properties:
    - identifer: string identifier of the text (e.g. "T789_something_important").
    - description: a short text explaining purpose of the experiment.
    - start_time: datetime when the experiment should start.
    - end_time: datetime when the experiment should stop.
    - default: required default `Alternative` to use before experiment is started.
    - winner: winning `Alternative` returned after the experiment has ended
    - version: integer version of the library
    - created_time: datetime when the experiment was created.

    Note: If `end_time` is not set - the experiment will run permanently.
    """

    identifier = models.SlugField(
        max_length=64,
        unique=True,
        help_text="Identifier can be made up from letters, digits, dashes and underscores.",
    )
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    default = models.ForeignKey('Alternative', blank=True, null=True, default=None, related_name='+')
    winner = models.ForeignKey('Alternative', blank=True, null=True, default=None, related_name='+')
    version = models.IntegerField(default=1)
    created_time = models.DateTimeField(auto_now=True)

    objects = ExperimentManager()

    @property
    def live(self):
        return self.start_time < timezone.now() and (self.end_time is None or self.end_time > timezone.now())

    @property
    def alternatives(self):
        return Alternative.objects.get_alternatives(self.identifier)

    @property
    def boundaries(self):
        """Returns a list with percentage boundaries within 100% range."""
        boundaries = []
        current = 0.0
        for alternative in self.alternatives:
            current += alternative.ratio
            boundaries.append(current)
        return boundaries

    def __unicode__(self):
        return unicode(self.identifier)

    def save(self, *args, **kwargs):
        super(Experiment, self).save(*args, **kwargs)
        clear_caches()

    def participant_count(self):
        return assignent_set.all().count()
    participant_count.admin_order_field = 'participant_count'

    def conversion_count(self):
        return assignent_set.filter(
            experiment=self,
            converted_time__isnull=False
        ).count()
    conversion_count.admin_order_field = 'conversion_count'


class AlternativeManager(models.Manager):
    use_for_related_fields = True

    def get_alternatives(self, experiment_id):
        """Tries to return alternatives list from cache.

        Return: dictionary, where keys are experiment ids:

          {
            'experiment_1': [<Object: Alternative1>, <Object: Alternative2>],
            ...
          }

        """
        now = timezone.now()
        self._local_cache_last_update = getattr(self, '_local_cache_last_update', now)
        if now - self._local_cache_last_update > timedelta(seconds=LOCAL_CACHE_LIFETIME) or not hasattr(self, '_alternatives'):
            alternatives = cache.get('experiments_alternatives')
            if not alternatives:
                list_of_alternatives = Alternative.objects.exclude(
                    experiment__default=None
                ).select_related('experiment').order_by('pk')
                alternatives = defaultdict(list)
                for alternative in list_of_alternatives:
                    alternatives[alternative.experiment.identifier].append(
                        alternative
                    )
                cache.set('experiments_alternatives', dict(alternatives))
            self._alternatives = alternatives
            self._local_cache_last_update = now
        return self._alternatives[experiment_id]


class Alternative(Model):
    """Represents an alternative in experiment.

    Properties:
    - experiment: instance of `Experiment` this alternative belongs to.
    - identifier: string identifier of the alternative.
    - ratio: float, part of the whole population that should be assigned to this alternative.
    - created_time: datetime when the alternative was created.
    """
    experiment = models.ForeignKey(Experiment)
    identifier = models.SlugField(
        max_length=16,
        help_text="Identifier can be made up from letters, digits, dashes and underscores.",
    )
    ratio = models.FloatField(
        default=1,
        help_text="Whole number ratio of participants that will be assigned into this alternative"
    )
    created_time = models.DateTimeField(auto_now=True)

    objects = AlternativeManager()

    def __unicode__(self):
        return unicode(self.identifier)

    def clean(self):
        """Validate data."""
        super(Alternative, self).clean()

        if self.ratio <= 0.0:
            raise exceptions.ValidationError(
                "Invalid ratio value '{ratio}', it must be more than 0.".format(ratio=self.ratio)
            )

        if float(int(self.ratio)) != self.ratio:
            raise exceptions.ValidationError(
                "Invalid ratio value '{ratio}', it must be a whole number.".format(ratio=self.ratio)
            )

    def save(self, *args, **kwargs):
        super(Alternative, self).save(*args, **kwargs)
        clear_caches()

    def participant_count(self):
        return self.assignment_set.all().count()
    participant_count.admin_order_field = 'participant_count'

    def conversion_count(self):
        return self.assignment_set.filter(
            converted_time__isnull=False,
        ).count()
    conversion_count.admin_order_field = 'conversion_count'


class Assignment(Model):
    ''' stores the identities that are participating in an experiment, and when they converted.'''
    experiment = models.ForeignKey(Experiment)
    identity = models.CharField(max_length=256)
    converted_time = models.DateTimeField(null=True, blank=True)

    # cached alt field. This could be calculated. Null means 'default'
    alternative = models.ForeignKey(Alternative, null=True, blank=True)


def clear_caches():
    if hasattr(Alternative.objects, '_alternatives'):
        del Alternative.objects._alternatives
    if hasattr(Experiment.objects, '_experiments'):
        del Experiment.objects._experiments
    cache.delete('experiments_experiments')
    cache.delete('experiments_alternatives')
