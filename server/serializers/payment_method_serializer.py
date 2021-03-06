# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework.serializers import ModelSerializer

from server.models import PaymentMethod


class PaymentMethodSerializer(ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = (
            'suffix',
            'card_type',
            'card_logo',
            'expiration_date',
        )
        read_only_fields = (
            'suffix',
            'card_type',
            'card_logo',
            'expiration_date',
        )
