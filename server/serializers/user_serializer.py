# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from idlecars import fields
from server import models


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'email',
        )
        read_only_fields = (
            'first_name',
            'last_name',
            'phone_number',
            'email',
        )

    phone_number = fields.PhoneNumberField(max_length=30, source='username')
