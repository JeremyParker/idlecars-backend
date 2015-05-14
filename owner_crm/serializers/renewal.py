# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from owner_crm import models


class Renewal(serializers.ModelSerializer):
    class Meta:
        model = models.Renewal

    def update(self, instance, validated_data):
        instance.state = validated_data.get('state')
        instance.save()
        return instance

    def validate_state(self, value):
        if value != models.Renewal.STATE_RENEWED:
            raise serializers.ValidationError('State can only be renewed')
        return value
