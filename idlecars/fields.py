# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils import timezone

from rest_framework import fields


def format_phone_number(raw):
    return "({}) {}-{}".format(raw[:3], raw[3:6], raw[6:])


def parse_phone_number(raw):
    return ''.join(x for x in raw if x.isdigit())


class PhoneNumberField(fields.CharField):
    def to_representation(self, obj):
        rep = super(PhoneNumberField, self).to_representation(obj)
        return format_phone_number(rep)

    def to_internal_value(self, data):
        value = parse_phone_number(super(PhoneNumberField, self).to_internal_value(data))
        if not len(value) == 10:
            raise ValidationError('Incorrect format. Expected a 10 digit US phone number.')
        return value


def format_date_array(date):
    ''' This method is public, so serializer method functions can use it '''
    return [date.year, date.month - 1, date.day]


class DateArrayField(fields.ListField):
    '''
    Field for a python date object that gets serialized as an array of integers for javascript. The
    format is [year, month, day]. The month is zero-indexed, so December is 11.
    '''
    child = fields.IntegerField(min_value=0)
    default_error_messages = {
        'invalid': 'Enter a valid date array.',
    }

    def get_value(self, dictionary):
        return super(DateArrayField, self).get_value(dictionary)

    def validate_empty_values(self, data):
        '''
        Override this method to interpret [] as a None value.
        '''
        if [] == data:
            return (True, None)
        return super(DateArrayField, self).validate_empty_values(data)

    def to_internal_value(self, data):
        if not isinstance(data, list) or len(data) != 3:
            self.fail('invalid')

        try:
            data = timezone.datetime(
                year=data[0],
                month=data[1] + 1,
                day=data[2],
                tzinfo=timezone.get_current_timezone(),
            )
        except (ValueError, TypeError):
            self.fail('invalid')
        return data

    def to_representation(self, value):
        return format_date_array(value)
