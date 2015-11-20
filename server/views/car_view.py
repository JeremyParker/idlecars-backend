# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins

from server.models import Car
from server.serializers import CarSerializer
from server.permissions import OwnsCar, IsAuthenticatedOwner


class CarViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CarSerializer
    model = Car

    def get_permissions(self):
        # special case for create: you just have to be an authenticated owner.
        if self.action == 'create':
            return (IsAuthenticatedOwner(),)
        return (OwnsCar(),)


    def get_queryset(self):
        owner = self.request.user.owner_set.first()
        return Car.objects.all().all().prefetch_related(
            'insurance',
            'make_model',
        ).filter(owner=owner)
