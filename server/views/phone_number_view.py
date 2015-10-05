# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response

from idlecars import fields

from server import models
from server.serializers import PhoneNumberSerializer


class PhoneNumberDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            driver = models.Driver.objects.get(auth_user__username=fields.parse_phone_number(pk))
        except models.Driver.DoesNotExist:
            # TODO(JP) create a new Driver, call start_set_password(auth_user).
            return Response('', status.HTTP_404_NOT_FOUND)

        serializer = PhoneNumberSerializer(driver.auth_user, many=False)
        return Response(serializer.data)
