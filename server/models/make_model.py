# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class MakeModel(models.Model):
    make = models.CharField(max_length=128, blank=True)
    model = models.CharField(max_length=128, blank=True)
    image_filename = models.CharField(max_length=128, blank=True)
    image_filenames = models.TextField(
        blank=True,
        help_text="Comma separated list of car image filenames. Each name must exist on our Amazon S3 bucket",
    )

    LUX_LEVEL_CHOICES = [
        (0, 'Standard'),
        (1, 'Luxury'),
    ]
    lux_level = models.IntegerField(choices=LUX_LEVEL_CHOICES, blank=True, null=True)

    BODY_TYPE_CHOICES = [
        (0, 'Sedan'),
        (1, 'SUV'),
    ]
    body_type = models.IntegerField(choices=BODY_TYPE_CHOICES, blank=True, null=True)


    def __unicode__(self):
        return '{} {}'.format(self.make, self.model)
