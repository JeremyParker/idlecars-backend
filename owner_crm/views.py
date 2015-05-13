# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import generics

import serializers

class UpdateRenewalView(generics.UpdateAPIView):
    serializer = serializers.Renewal
