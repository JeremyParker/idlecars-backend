# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response

from server import models
from server.serializers import BookingDetailsSerializer
from server.permissions import OwnsBooking


class CancelationView(APIView):
    def get_permissions(self):
        return (OwnsBooking()),

    def post(self, request, format=None):
    # def post(self, request, pk, format=None):
        import pdb; pdb.set_trace()
        try:
            booking = models.Booking.objects.get(pk=pk)
        except models.Booking.DoesNotExist:
            raise Http404

        # TODO: cancel the booking, store the action... whatever
        serializer = BookingDetailsSerializer(booking, many=False)
        return Response(serializer.data)
