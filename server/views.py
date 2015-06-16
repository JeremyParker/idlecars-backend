# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import login, logout
from django.contrib.auth import models as auth_models

from rest_framework import viewsets, mixins
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

import models
import authentication
import services.car
from serializers import CarSerializer, BookingSerializer, DriverSerializer, AuthUserSerializer
from permissions import OwnsDriver, OwnsBooking


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = services.car.listing_queryset
    serializer_class = CarSerializer


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, OwnsBooking,)
    serializer_class = BookingSerializer
    queryset = models.Booking.objects.all()

    def get_permissions(self):
        return (IsAuthenticated() if self.request.method == 'POST' else OwnsBooking()),

    def perform_create(self, serializer):

        driver = models.Driver.objects.get(auth_user=self.request.user)
        serializer.save(driver=driver)


class DriverViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = DriverSerializer
    model = models.Driver
    queryset = models.Driver.objects.all()

    def get_permissions(self):
        # allow non-authenticated user to create a Driver
        return (AllowAny() if self.request.method == 'POST' else OwnsDriver()),

    def get_object(self):
        ''' override to map 'me' to the current user's driver object '''
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.request.user.is_authenticated() and self.kwargs[lookup_url_kwarg] == 'me':
            self.kwargs[lookup_url_kwarg] = models.Driver.objects.get(auth_user=self.request.user).pk
        return super(DriverViewSet, self).get_object()
