# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from rest_framework import viewsets, mixins

from server.models import Car, Owner
from server.services import car as car_service
from server.serializers import CarSerializer
from server.permissions import OwnsCar, IsAuthenticatedOwner

CAR_NOT_FOUND = 'Sorry, this license plate isn\'t in the TLC database. Please check your plate number and try again.'
CAR_ALREADY_REGISTERED = 'This car is already registered with idlecars. Please call for support at {}'.format(
    settings.IDLECARS_PHONE_NUMBER
)

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
        return (IsAuthenticatedOwner(), OwnsCar(),)

    def get_queryset(self):
        owner = self.request.user.owner_set.first()
        queryset = Car.objects.all().all().select_related(
            'insurance',
            'make_model',
        )
        if self.action == 'list':
            return queryset.filter(owner=owner)
        return queryset

    def perform_create(self, serializer):
        owner = Owner.objects.get(auth_users=self.request.user)
        plate = serializer.validated_data.get('plate')
        try:
            new_car = car_service.create_car(owner, plate)
        except car_service.CarTLCException:
            return Response({'_app_notifications': [CAR_NOT_FOUND]}, HTTP_400_BAD_REQUEST)
        except car_service.CarDuplicate:
            return Response({'_app_notifications': [CAR_ALREADY_REGISTERED]}, HTTP_400_BAD_REQUEST)

        serializer.instance = new_car
