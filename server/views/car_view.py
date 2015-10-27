# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins
from rest_framework.response import Response

from server.models import Car
from server.services import car as car_service
from server.serializers import CarSerializer

class CarViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = CarSerializer

    def get_queryset(self):
        return car_service.filter_listable(Car.objects.all())

    def list(self, request, *args, **kwargs):
        queryset = car_service.filter_live(
            self.filter_queryset(self.get_queryset())
        ).order_by('solo_cost')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
