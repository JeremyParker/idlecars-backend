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

    def __unicode__(self):
        return '{} {}'.format(self.make, self.model)
