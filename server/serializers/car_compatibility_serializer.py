# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from server.models import RideshareProvider

class CarCompatibilitySerializer(serializers.Serializer):
    uber_x = serializers.SerializerMethodField()

    def get_uber_x(self, obj):
        return RideshareProvider.objects.get(friendly_id='uber_x').name if obj.uber_x else None
