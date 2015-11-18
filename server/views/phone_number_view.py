# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from idlecars import fields

from server import models
from server.serializers import PhoneNumberSerializer


class PhoneNumberDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            user = User.objects.get(username=fields.parse_phone_number(pk))
        except User.DoesNotExist:
            # TODO(JP) create a new Driver, call start_set_password(auth_user).
            return Response('', status.HTTP_404_NOT_FOUND)

        serializer = PhoneNumberSerializer(user, many=False)
        return Response(serializer.data)
