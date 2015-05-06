# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

import models
import services.car
from serializers import CarSerializer, BookingSerializer


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = services.car.listing_queryset
    serializer_class = CarSerializer


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides `create` action

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass

class CreateBookingView(CreateViewSet):
    serializer_class = BookingSerializer
    queryset = models.Booking.objects.all()
