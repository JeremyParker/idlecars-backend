# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from server.models import Owner


class OwnerSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()

    class Meta:
        model = Owner
        fields = (
            'address',
            'phone_number',
            'name',
        )
        read_only_fields = (
            'address',
            'phone_number',
            'name',
        )

    def get_address(self, obj):
        return 'Some Address'

    def get_address(self, obj):
        return 'Some Address'
