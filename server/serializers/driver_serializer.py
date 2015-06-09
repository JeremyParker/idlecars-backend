# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from rest_framework import serializers

from server import models


class DriverSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=20)

    class Meta:
        model = models.Driver

    def update(self, instance, validated_data):
        user_account = instance.user_account

        if validated_data.get('phone_number'):
            user_account.phone_number = validated_data.get('phone_number')

        user_account.save()

        return instance
