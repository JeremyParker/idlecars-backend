# -*- encoding:utf-8 -*-
from __future__ import unicode_literals


from rest_framework import viewsets

from server.services import car as car_service
from server.serializers import CarSerializer

class CarViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CarSerializer

    def get_queryset(self):
        return car_service.get_listing_queryset().order_by('solo_cost')
