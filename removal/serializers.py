# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework.serializers import ModelSerializer

from removal import models


class RemovalSerializer(ModelSerializer):
    class Meta:
        model = models.Removal
        fields = (
            'id',
            'first_name',
            'last_name',
            'hack_license_number',
        )
        read_only_fields = (
            'id',
        )
