# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import auth
from django.core.exceptions import PermissionDenied

from rest_framework.serializers import ModelSerializer, CharField, EmailField, ValidationError
from rest_framework.serializers import SerializerMethodField
from rest_framework.exceptions import ValidationError

from idlecars import fields
from server import models
from server.serializers import PaymentMethodSerializer, CreditCodeSerializer
from server.services import driver as driver_service
from server.services import ServiceError
from server.services import auth_user as auth_user_service


class DriverSerializer(ModelSerializer):
    # we must add fields that are mapped to auth_user, or auth_user.customer
    phone_number = fields.PhoneNumberField(max_length=30)
    password = CharField(max_length=128, write_only=True)
    email = EmailField(required=False, allow_blank=True)
    first_name = CharField(max_length=30, required=False, allow_blank=True)
    last_name = CharField(max_length=30, required=False, allow_blank=True)

    invitor_code = CharField(max_length=16, required=False, allow_blank=True, write_only=True)

    payment_method = SerializerMethodField()
    app_credit = SerializerMethodField()
    invite_code = SerializerMethodField()

    class Meta:
        model = models.Driver
        fields = (
            'id',
            'driver_license_image',
            'fhv_license_image',
            'address_proof_image',
            'all_docs_uploaded',

            # stuff from auth_user TOOD - remove User fields
            'phone_number',
            'password',
            'invitor_code',
            'email',
            'first_name',
            'last_name',
            'ssn',
            'sms_enabled',
            'client_display',
            'payment_method',
            'app_credit',
            'invite_code',
        )
        read_only_fields = (
            'id',
            'all_docs_uploaded',
            'payment_method',
            'app_credit',
            'invite_code',
        )

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        try:
            auth_user = auth.models.User.objects.get(username=phone_number)
            # TODO(JP): allow driver creation if you are authrorized as this user
            raise ValidationError("This phone number already has a user.")
        except auth.models.User.DoesNotExist:
            password = validated_data.get('password')
            auth_user = auth.models.User.objects.create_user(
                username=phone_number,
                password=password,
            )
        return driver_service.create(auth_user=auth_user)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            raise PermissionDenied()

        # All Taxi isn't doing a referral credit program at launch.
        # if 'invitor_code' in validated_data and validated_data['invitor_code']:
        #     try:
        #         driver_service.redeem_code(instance, validated_data['invitor_code'])
        #     except ServiceError as e:
        #         raise ValidationError(e.message)

        instance.ssn = validated_data.get('ssn', instance.ssn)
        instance.driver_license_image = validated_data.get('driver_license_image', instance.driver_license_image)
        instance.fhv_license_image = validated_data.get('fhv_license_image', instance.fhv_license_image)
        instance.address_proof_image = validated_data.get('address_proof_image', instance.address_proof_image)
        instance.sms_enabled = validated_data.get('sms_enabled', instance.sms_enabled)
        instance.save()

        return instance

    def get_payment_method(self, instance):
        payment_method = driver_service.get_default_payment_method(instance)
        if payment_method:
            return PaymentMethodSerializer(payment_method).data

    def get_app_credit(self, instance):
        return '${}'.format(instance.app_credit())

    def get_invite_code(self, instance):
        if instance.invite_code():
            return CreditCodeSerializer(instance.invite_code()).data
