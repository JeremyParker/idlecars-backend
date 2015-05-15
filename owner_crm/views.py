# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins

import serializers, models


class UpdateRenewalView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.Renewal.objects.all()
    serializer_class = serializers.Renewal
    lookup_field = 'token'
