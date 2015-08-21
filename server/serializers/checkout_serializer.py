# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers


class CheckoutSerializer(serializers.Serializer):
    nonce = serializers.CharField(max_length=512)
