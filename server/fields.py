# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from rest_framework import fields

from server.models import Car

class CarColorField(fields.CharField):
    def to_representation(self, obj):
        return dict(Car.COLOR_CHOICES)[obj]

    def to_internal_value(self, data):
        inverse_dict = {v.lower(): k for k, v in Car.COLOR_CHOICES}
        try:
            value = inverse_dict[data.lower()]
        except KeyError:
            raise ValidationError('Sorry, that isn\'t a supported color name')
        return value
