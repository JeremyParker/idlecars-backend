# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from server.models import Car


class CarBaseSerializer(ModelSerializer):
    class Meta:
        model = Car
        fields = ()
        read_only_fields = ()
