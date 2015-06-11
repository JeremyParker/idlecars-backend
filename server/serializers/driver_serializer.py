# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from rest_framework import serializers

from server import models


class DriverSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=20)

    class Meta:
        model = models.Driver
        fields = (
            'driver_license_image',
            'fhv_license_image',
            'address_proof_image',
            'defensive_cert_image',
            'phone_number',
            )

    def update(self, instance, validated_data):
        user_account = instance.user_account

        user_account.phone_number = validated_data.get('phone_number', user_account.phone_number)
        user_account.save()

        instance.driver_license_image = validated_data.get('driver_license_image', instance.driver_license_image)
        instance.fhv_license_image = validated_data.get('fhv_license_image', instance.fhv_license_image)
        instance.address_proof_image = validated_data.get('address_proof_image', instance.address_proof_image)
        instance.defensive_cert_image = validated_data.get('defensive_cert_image', instance.defensive_cert_image)
        instance.save()

        return instance
