# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from server.models import RideshareFlavor

class CarCompatibilitySerializer(serializers.Serializer):
    uber_x = serializers.SerializerMethodField()

    def get_uber_x(self, obj):
        return self._rideshare_flavor_name('uber_x') if obj.uber_x() else None

    def _rideshare_flavor_name(self, friendly_id):
        try:
            return RideshareFlavor.objects.get(friendly_id=friendly_id).name
        except RideshareFlavor.DoesNotExist:
            return None
