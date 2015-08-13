# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from server import models
from server.services import booking as booking_service
from server.serializers import BookingSerializer, BookingDetailsSerializer
from server.permissions import OwnsBooking


class BookingViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'partial_update']:
            return BookingDetailsSerializer
        return BookingSerializer

    def get_permissions(self):
        return (IsAuthenticated() if self.request.method == 'POST' else OwnsBooking()),

    def perform_create(self, serializer):
        driver = models.Driver.objects.get(auth_user=self.request.user)
        serializer.save(driver=driver)

    def get_queryset(self):
        return models.Booking.objects.filter(
            driver=models.Driver.objects.get(auth_user=self.request.user),
            state__in=models.booking_state.visible_states()
        )

    @detail_route(methods=['post'], permission_classes=[OwnsBooking])
    def cancelation(self, request, pk=None):
        booking = self.get_object()
        if booking.state not in models.booking_state.cancelable_states():
            raise ValidationError('This rental can\'t be canceled at this time.')
        serializer = self.get_serializer(booking_service.cancel_booking(booking))
        return Response(serializer.data)

