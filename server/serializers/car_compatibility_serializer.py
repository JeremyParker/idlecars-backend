# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

class CarCompatibilitySerializer(serializers.Serializer):
    uber_x = serializers.CharField(max_length=200)
