# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.serializers import Serializer
from rest_framework.response import Response

from idlecars import fields

from server.models import Owner


class PhoneNumberSerializer(Serializer):
    phone_number = fields.PhoneNumberField(max_length=30, source='username')


class PhoneNumberDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            auth_user = User.objects.get(username=fields.parse_phone_number(pk))
            # TODO - check if there is an Owner objects associated with this User

        except User.DoesNotExist:
            # TODO(JP) this would be where we send them an SMS and invite them to set a password
            raise Http404

        serializer = PhoneNumberSerializer(auth_user, many=False)
        return Response(serializer.data)
