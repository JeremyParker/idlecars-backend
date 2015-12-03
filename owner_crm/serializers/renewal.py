# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from rest_framework import serializers

from owner_crm.models import ConsumableToken, Renewal
from server import models as server_models


class Renewal(serializers.ModelSerializer):
    class Meta:
        model = Renewal

    def update(self, instance, validated_data):
        car = instance.car
        car.last_status_update = timezone.now()
        car.save()

        instance.state = validated_data.get('state')
        instance.save()
        return instance

    def validate_state(self, value):
        if value != ConsumableToken.STATE_CONSUMED and value != ConsumableToken.STATE_RETRACTED:
            raise serializers.ValidationError('State can only be consumed, or retraced')
        return value
