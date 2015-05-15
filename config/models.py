# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

# TODO: JSON support
# import simplejson as json

from django.db import models


class Config(models.Model):
    INTEGER_TYPE = 0
    FLOATING_TYPE = 0
    STRING_TYPE = 0
    JSON_TYPE = 0
    BOOLEAN_TYPE = 0

    TYPES = (
        (INTEGER_TYPE, 'Integer'),
        (FLOATING_TYPE, 'Float'),
        (STRING_TYPE, 'String'),
        (JSON_TYPE, 'JSON'),
        (BOOLEAN_TYPE, 'Boolean'),
    )
    data_type = models.IntegerField(choices=TYPES, default=INTEGER_TYPE)
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True)
    units = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)

    def get_data(self):
        parsers = {
            INTEGER_TYPE: int,
            FLOATING_TYPE: float,
            STRING_TYPE: unicode,
            JSON_TYPE: json.loads,
            BOOLEAN_TYPE: json.loads,
        }

        return parsers[self.data_type](self.value)

    def clean(self):
        super(Config, self).clean()

        if self.data_type:
            try:
                self.get_data()
            except:
                raise exceptions.ValidationError("%s is not a valid %s" % (repr(self.value), TYPES[self.data_type][1]))
