# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework.serializers import ModelSerializer

from server import models
from server.serializers import UserSerializer


class OwnerSerializer(ModelSerializer):
    auth_users = UserSerializer(many=True, read_only=True)
    class Meta:
        model = models.Driver
        fields = (
            'id',
            'auth_users',
        )
        read_only_fields = ('id', 'auth_users',)
