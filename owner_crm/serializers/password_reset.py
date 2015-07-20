# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from server import models, fields


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=40)
    password = serializers.CharField(max_length=128)
