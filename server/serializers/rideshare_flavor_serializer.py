# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from server.models import RideshareFlavor

class RideshareFlavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideshareFlavor
        fields = (
            'name',
            'friendly_id',
        )
