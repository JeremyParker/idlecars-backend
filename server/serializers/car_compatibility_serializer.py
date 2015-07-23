# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

class CarCompatibilitySerializer(serializers.Serializer):
    uber_x = serializers.SerializerMethodField()

    def get_uber_x(self, obj):
        return 'uberX' if obj.uber_x else None
