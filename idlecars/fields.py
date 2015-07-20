# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import six

from django.core.exceptions import ValidationError

from rest_framework import serializers


def format_phone_number(raw):
    return "({}) {}-{}".format(raw[:3], raw[3:6], raw[6:])


def parse_phone_number(raw):
    return ''.join(x for x in raw if x.isdigit())


class PhoneNumberField(serializers.CharField):
    def to_representation(self, obj):
        rep = super(PhoneNumberField, self).to_representation(obj)
        return format_phone_number(rep)

    def to_internal_value(self, data):
        value = parse_phone_number(super(PhoneNumberField, self).to_internal_value(data))
        if not len(value) == 10:
            raise ValidationError('Incorrect format. Expected a 10 digit US phone number.')
        return value
