# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework.serializers import Serializer

from server import fields

class PhoneNumberSerializer(Serializer):
    phone_number = fields.PhoneNumberField(max_length=30)
