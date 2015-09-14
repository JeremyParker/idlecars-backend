# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

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
            created, auth_user = owner_service.invite_legacy_owner(phone_number)
        except Owner.DoesNotExist:
            content = {'_app_notifications': [
                '''
                Sorry, something went wrong. We couldn't find a record of you as a car-owner
                in our system. Please contact idlecars, to set up your owner account.
                '''
            ],}
            return Response(content, status.HTTP_404_NOT_FOUND)

        if created:
            content = PhoneNumberSerializer(auth_user).data
            content.update({'_app_notifications': [
                '''
                Great, you're in our system already! An email has been sent to your address
                with instructions for setting your password.
                '''
            ],})
            return Response(content, status.HTTP_404_NOT_FOUND)
        else:
            serializer = PhoneNumberSerializer(auth_user)
            return Response(serializer.data, status.HTTP_200_OK)
