# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from credit import models


class CreditCodeSerializer(ModelSerializer):
    expiry_time = SerializerMethodField()
    credit_amount = SerializerMethodField()
    invitor_credit_amount = SerializerMethodField()

    class Meta:
        model = models.CreditCode
        fields = (
            'id',
            'credit_code',
            'expiry_time',
            'redeem_count ',
            'credit_amount',
            'invitor_credit_amount',
        )

        read_only_fields = (
            'id',
            'credit_code',
            'expiry_time',
            'redeem_count ',
            'credit_amount',
            'invitor_credit_amount',
        )

    def get_expiry_time(self, instance):
        if instance.expiry_time:
            return instance.expiry_time.strftime('%b %d')

    def get_credit_amount(self, instance):
        return '${}'.format(instance.credit_amount)

    def get_invitor_credit_amount(self, instance):
        return '${}'.format(instance.invitor_credit_amount)
