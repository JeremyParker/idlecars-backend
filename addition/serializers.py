# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework.serializers import ModelSerializer

from addition import models


class AdditionSerializer(ModelSerializer):
    class Meta:
        model = models.Addition
        fields = (
            'id',
            'plate',
            'phone_number',
            'email',
            'first_name',
            'last_name',
            'ssn',
            'driver_license_image',
            'fhv_license_image',
            'address_proof_image',
        )
        read_only_fields = (
            'id',
        )
