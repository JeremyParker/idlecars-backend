# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from server.models import Payment
from server.serializers import payment_method_serializer


class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    payment_method = payment_method_serializer.PaymentMethodSerializer(many=False, read_only=True)

    class Meta:
        model = Payment
        fields = (
            'amount',
            'status',
            'created_time',
            'payment_method',
        )
        read_only_fields = (
            'amount',
            'status',
            'created_time',
            'payment_method',
        )

    def get_status(self, obj):
        return obj.status_string()
