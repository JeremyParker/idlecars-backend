# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins

import serializers


class UpdateRenewalView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer = serializers.Renewal
