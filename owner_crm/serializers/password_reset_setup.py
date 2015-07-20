# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from idlecars import fields
from server import models


class PasswordResetSetupSerializer(serializers.Serializer):
    phone_number = fields.PhoneNumberField(max_length=30)
