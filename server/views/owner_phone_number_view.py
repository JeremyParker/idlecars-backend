# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from idlecars import fields

from server.services import owner_service
from server.models import Owner
from server.permissions import OwnsOwner
from server.serializers import PhoneNumberSerializer


class OwnerPhoneNumberDetailView(APIView):
    def get(self, request, pk, format=None):
        phone_number = fields.parse_phone_number(pk)
        try:
            auth_user = User.objects.get(username=phone_number)
            owner = Owner.objects.get(auth_users=auth_user)
        except (Owner.DoesNotExist, User.DoesNotExist):
            return Response('', status.HTTP_404_NOT_FOUND)

        content = PhoneNumberSerializer(auth_user).data
        serializer = PhoneNumberSerializer(auth_user)
        return Response(serializer.data, status.HTTP_200_OK)
