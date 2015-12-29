# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer, CharField, ValidationError
from rest_framework.serializers import PrimaryKeyRelatedField, SerializerMethodField

from idlecars import fields
from server import models
from server.services import auth_user as auth_user_service
from server.services import driver as driver_service


user_fields = (
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'driver',
            'owner',
        )


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = user_fields
        read_only_fields = ('id', 'driver' 'owner',)

    phone_number = fields.PhoneNumberField(max_length=30, source='username')
    driver = PrimaryKeyRelatedField(read_only=True)
    owner = SerializerMethodField(read_only=True)

    def get_owner(self, obj):
        try:
            # We don't support multiple owners per user.
            return obj.owner_set.first().pk
        except AttributeError:
            return None

    def update(self, instance, validated_data):
        had_email = bool(instance.email)
        auth_user_service.update(instance, validated_data)
        if instance.email and not had_email:
            if instance.owner_set.exists():
                pass # TODO: hookup the owner welcome email here.
            elif getattr(instance, 'driver', None):
                driver_service.on_set_email(instance.driver)

        return instance


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
