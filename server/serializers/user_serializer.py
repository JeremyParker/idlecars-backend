# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, CharField, ValidationError
from rest_framework.serializers import PrimaryKeyRelatedField

from idlecars import fields
from server import models

user_fields = (
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'driver',
            # 'owner',
        )


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = user_fields
        read_only_fields = ('id', 'driver')

    phone_number = fields.PhoneNumberField(max_length=30, source='username')
    driver = PrimaryKeyRelatedField(read_only=True)
    # owners = PrimaryKeyRelatedField(read_only=True)


class UserCreateSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('password',)
        read_only_fields = UserSerializer.Meta.read_only_fields + ('password',)

    password = CharField(max_length=128, write_only=True)

    def create(self, validated_data):
        username = validated_data.get('username')
        try:
            auth_user = User.objects.get(username=username)
            raise ValidationError("This phone number already has a user.")
        except User.DoesNotExist:
            password = validated_data.get('password')
            auth_user = User.objects.create_user(
                username=username,
                password=password,
            )
        return auth_user
