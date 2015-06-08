# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from server.models import UserAccount


class UserAccountSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = UserAccount

    def create(self, validated_data):
        return UserAccount.objects.create(**validated_data)
