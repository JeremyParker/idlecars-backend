# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class StrippedCharField(models.CharField):
    def get_prep_value(self, value):
        val = super(StrippedCharField, self).get_prep_value(value)
        if val is not None:
            return val.strip()
        else:
            return None


class Choices(object):
    def __init__(self, **kwargs):
        self._choices_dict = kwargs
        self._choices_list = sorted(kwargs.items())  # Sorted so we iterate alphabetically
        for k in self._choices_dict.keys():
            setattr(self, k.upper(), k)

    def __getitem__(self, key):
        return self._choices_dict[key]

    def __iter__(self):
        return iter(self._choices_list)

    def __len__(self):
        return len(self._choices_list)

    def keys(self):
        return self._choices_dict.keys()


class Choice(unicode):
    def __new__(cls, value, choices=None):
        instance = super(Choice, cls).__new__(cls, value)
        return instance

    def __init__(self, value, choices):
        for name, _ in choices:
            setattr(self, 'is_' + name, self == name)


class ChoiceField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        return Choice(value, choices=self.choices)
