# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404

from rest_framework.views import APIView
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

import models, services, fields
from serializers import CarSerializer, BookingSerializer, BookingDetailsSerializer
from serializers import DriverSerializer, PhoneNumberSerializer
from permissions import OwnsDriver, OwnsBooking


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = services.car.listing_queryset
    serializer_class = CarSerializer


class BookingViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return BookingDetailsSerializer
        return BookingSerializer

    def get_permissions(self):
        return (IsAuthenticated() if self.request.method == 'POST' else OwnsBooking()),

    def perform_create(self, serializer):
        driver = models.Driver.objects.get(auth_user=self.request.user)
        serializer.save(driver=driver)

    def get_queryset(self):
        driver = models.Driver.objects.get(auth_user=self.request.user)
        return models.Booking.objects.filter(driver=driver)


class DriverViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):
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


class PhoneNumberDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            driver = models.Driver.objects.get(auth_user__username=fields.parse_phone_number(pk))
        except models.Driver.DoesNotExist:
            # TODO(JP) create a new Driver, call start_set_password(auth_user).
            raise Http404

        serializer = PhoneNumberSerializer(driver, many=False)
        return Response(serializer.data)
