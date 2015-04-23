# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

import models
from serializers import CarSerializer, BookingSerializer


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'cars': reverse('car-list', request=request, format=format),
    })


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Car.objects.filter(
        owner__isnull=False,
        make_model__isnull=False,
        year__isnull=False,
        solo_cost__isnull=False,
        solo_deposit__isnull=False,
    ).exclude(
        min_lease='_00_unknown',
    ).exclude(
        status='unknown',
    ).exclude(
        next_available_date__isnull=True,
        status='busy',
    ).exclude(
         plate='',
    ).exclude(
         base='',
    ).exclude(
        owner__city='',
    ).exclude(
        owner__state_code='',
    )
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
