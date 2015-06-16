# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import models as auth_models
from rest_framework import serializers


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth_models.User
        fields = (
            'id',
            'phone_number',
            'password',
            'first_name',
            'last_name',
            'email'
        )
        read_only_fields = ('id',)
        write_only_fields = ('password',)

    phone_number = serializers.CharField(source='username')

    def create(self, validated_data):
        instance = super(AuthUserSerializer, self).create(validated_data)
        instance.set_password(validated_data['password'])
        return instance

    def update(self, instance, validated_data):
        instance = super(AuthUserSerializer, self).update(instance, validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        update_session_auth_hash(self.context.get('request'), instance)            
        return instance
