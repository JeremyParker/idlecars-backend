# -*- encoding:utf-8 -*-
from __future__ import unicode_literals


from rest_framework import viewsets

from server import services
from server.serializers import CarSerializer

class CarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = services.car.listing_queryset.order_by('solo_cost')
    serializer_class = CarSerializer
