# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from owner_crm import models


class Renewal(serializers.ModelSerializer):
    class Meta:
        model = models.Renewal

    def update(self, instance, validated_data):
        if validated_data.get('state') == 'Renewed':
            instance.state = models.Renewal.STATE_RENEWED

        return instance
