# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from idlecars import rest_helpers
from server import models
from server.services import ServiceError
from server.services import booking as booking_service
from server.serializers import BookingSerializer, BookingDetailsSerializer
from server.permissions import OwnsBooking


class BookingViewSet(
        rest_helpers.ICCreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):

    def get_serializer_class(self):
        detail_actions = ['list', 'retrieve', 'partial_update', 'checkout', 'cancelation', 'pickup']
        if self.action in detail_actions:
            return BookingDetailsSerializer
        return BookingSerializer

    def get_permissions(self):
        return (IsAuthenticated() if self.request.method == 'POST' else OwnsBooking()),

    def perform_create(self, serializer):
        driver = models.Driver.objects.get(auth_user=self.request.user)
        serializer.save(driver=driver)

    def get_queryset(self):
        return booking_service.filter_visible(models.Booking.objects.filter(
            driver=models.Driver.objects.get(auth_user=self.request.user),
        ))

    @detail_route(methods=['post'], permission_classes=[OwnsBooking])
    def cancelation(self, request, pk=None):
        booking = self.get_object()
        try:
            booking = booking_service.cancel(booking)
            return Response(self.get_serializer(booking).data, HTTP_201_CREATED)
        except ServiceError as booking_error:
            return Response({'_app_notifications': [booking_error.message]}, HTTP_400_BAD_REQUEST)
