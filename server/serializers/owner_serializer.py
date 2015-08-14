# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from idlecars import fields
from server.models import Owner


class OwnerSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    phone_number = fields.PhoneNumberField(max_length=30)

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
