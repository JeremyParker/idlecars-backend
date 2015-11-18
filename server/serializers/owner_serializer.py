# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from idlecars import fields
from server.models import Owner
from server import models
from server.serializers import UserSerializer


class OwnerContactSerializer(ModelSerializer):
    '''
    Used for showing a driver the contact info for an owner
    '''
    address = SerializerMethodField()
    phone_number = fields.PhoneNumberField(max_length=30)

    class Meta:
        model = Owner
        fields = (
            'id',
            'address',
            'phone_number',
            'name',
            'sms_enabled',
        )
        read_only_fields = (
            'id',
            'address',
            'phone_number',
            'name',
        )

    def get_address(self, obj):
        return '{}\n{}\n{}, {} {}'.format(
            obj.address1,
            obj.address2,
            obj.city,
            obj.state_code,
            obj.zipcode,
        )


class OwnerSerializer(ModelSerializer):
    auth_users = UserSerializer(many=True, read_only=True)
    class Meta:
        model = models.Owner
        fields = (
            'id',
            'auth_users',
            'sms_enabled',
            'company_name',
            'address1',
            'address2',
            'city',
            'state_code',
            'zipcode',
            # 'bank_account_status', TODO
        )
        read_only_fields = ('id', 'auth_users',)
