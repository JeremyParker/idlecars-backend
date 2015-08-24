# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from server import models
from server.services import booking as booking_service
from server.serializers import BookingSerializer, BookingDetailsSerializer, CheckoutSerializer
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
        return booking_service.filter_visible(models.Booking.objects.filter(
            driver=models.Driver.objects.get(auth_user=self.request.user),
        ))

    @detail_route(methods=['post'], permission_classes=[OwnsBooking])
    def cancelation(self, request, pk=None):
        booking = self.get_object()
        if not booking_service.can_cancel(booking):
            raise ValidationError('Your rental can\'t be canceled at this time.')
        serializer = self.get_serializer(booking_service.cancel(booking))
        return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[OwnsBooking])
    def checkout(self, request, pk=None):
        serializer = CheckoutSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        booking = self.get_object()
        if not booking_service.can_checkout(booking):
            raise ValidationError('Your rental can\'t be created at this time.')

        nonce = serializer.validated_data['nonce']
        result_booking = booking_service.checkout(booking, nonce=nonce)
        result_serializer = self.get_serializer(result_booking)
        return Response(result_serializer.data)

    @detail_route(methods=['post'], permission_classes=[OwnsBooking])
    def pickup(self, request, pk=None):
        booking = self.get_object()
        if not booking_service.can_pickup(booking):
            raise ValidationError('Your rental can\'t be picked up at this time.')
        serializer = self.get_serializer(booking_service.pickup(booking))
        return Response(serializer.data)

