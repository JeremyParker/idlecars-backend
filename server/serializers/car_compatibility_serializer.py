# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from server.models import RideshareFlavor

class CarCompatibilitySerializer(serializers.Serializer):
    uber_x = serializers.CharField()
    uber_plus = serializers.CharField()
    uber_black = serializers.CharField()
    uber_suv = serializers.CharField()
    uber_lux = serializers.CharField()
    lyft_standard = serializers.CharField()
    lyft_suv = serializers.CharField()
    via_standard = serializers.CharField()
    via_suv = serializers.CharField()
    gett_standard = serializers.CharField()
    gett_suv = serializers.CharField()
