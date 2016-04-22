# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.serializers import ValidationError

from server.models import Car, Owner
from server.services import car as car_service
from server.services import ServiceError
from server.serializers import CarSerializer, CarCreateSerializer
from server.permissions import OwnsCar, IsAuthenticatedOwner

CAR_NOT_FOUND = 'Sorry, this medallion isn\'t in the TLC database. Please check your medallion number and try again.'

class CarViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    model = Car

    def get_serializer_class(self):
        if self.action == 'create':
            return CarCreateSerializer
        return CarSerializer

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
            return queryset.filter(owner=owner).exclude(plate='')
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            return super(CarViewSet, self).create(request, *args, **kwargs)
        except car_service.CarTLCException:
            return Response({'_app_notifications': [CAR_NOT_FOUND]}, status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        owner = Owner.objects.get(auth_users=self.request.user)
        plate = serializer.validated_data.get('plate').upper()
        new_car = car_service.create_car(owner, plate)
        serializer.instance = new_car

    def update(self, request, *args, **kwargs):
        if 'insurance' in request.data:
            if request.data['insurance'] == 'approved':
                car_service.insurance(car=self.get_object(), approved=True)
            elif request.data['insurance'] == 'rejected':
                car_service.insurance(car=self.get_object(), approved=False)
        if 'return_confirmation' in request.data:
            try:
                car_service.return_confirm(car=self.get_object())
            except ServiceError as e:
                return Response({'_app_notifications': [e.detail]}, status.HTTP_400_BAD_REQUEST)
        try:
            return super(CarViewSet, self).update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'_app_notifications': e.detail.values()[0]}, status.HTTP_400_BAD_REQUEST)
        except ServiceError as e:
            return Response({'_app_notifications': [e.message]}, status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        '''
        any time we update something on this car through this view, it means the owner
        interacted with the car. From that we can conclude that the status of the car is up
        to date. Otherwise they would have changed it. We're overriding this method to set
        the last status update time to now.
        '''
        serializer.validated_data.update({'last_status_update': timezone.now()})
        super(CarViewSet, self).perform_update(serializer)

    @detail_route(methods=['post'], permission_classes=[OwnsCar])
    def extension(self, request, pk=None):
        car = self.get_object()
        car.last_status_update = timezone.now()
        car.save()
        data = self.get_serializer(car).data
        data.update({'_app_notifications': [{'success': 'Your listing has been extended'},],})
        return Response(data, status.HTTP_201_CREATED)
