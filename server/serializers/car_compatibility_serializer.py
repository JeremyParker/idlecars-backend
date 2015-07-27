# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from server.models import RideshareProvider

class CarCompatibilitySerializer(serializers.Serializer):
    uber_x = serializers.SerializerMethodField()

    def get_uber_x(self, obj):
        return self._rideshare_provider_name('uber_x') if obj.uber_x() else None

    def _rideshare_provider_name(self, friendly_id):
        try:
            return RideshareProvider.objects.get(friendly_id=friendly_id).name
        except RideshareProvider.DoesNotExist:
            return None
