# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404

from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.exceptions import ValidationError

from server import models
from server.services import payment_method as payment_method_service
from server.services import driver as driver_service
from server.serializers import DriverSerializer, NonceSerializer
from server.permissions import OwnsDriver

DRIVER_NOT_FOUND_ERROR = 'Sorry, something went wrong. Please reload the webpage and try again.'


class DriverViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):
    serializer_class = DriverSerializer
    model = models.Driver
    queryset = models.Driver.objects.all().select_related('auth_user')

    def get_permissions(self):
        # TODO - don't allow non-authenticated user to create a Driver
        return (AllowAny() if self.request.method == 'POST' else OwnsDriver()),

    def get_object(self):
        ''' override to map 'me' to the current user's driver object '''
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.request.user.is_authenticated() and self.kwargs[lookup_url_kwarg] == 'me':
            try:
                me_pk = models.Driver.objects.get(auth_user=self.request.user).pk
                self.kwargs[lookup_url_kwarg] = me_pk
            except models.Driver.DoesNotExist:
                ''' we're creating a driver here because in the DriverApp client, an owner can
                log in, but fails when they try to get their Driver object. '''
                return driver_service.create(auth_user=self.request.user)
        return super(DriverViewSet, self).get_object()

    def update(self, request, *args, **kwargs):
        try:
            return super(DriverViewSet, self).update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'_app_notifications': [e.detail]}, status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'], permission_classes=[OwnsDriver])
    def payment_method(self, request, pk=None):
        serializer = NonceSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response({'_app_notifications': serializer.errors}, status=HTTP_400_BAD_REQUEST)
        try:
            driver = self.get_object()
            nonce = serializer.validated_data['nonce']
            payment_method_service.add_payment_method(driver, nonce)
            result_serializer = self.get_serializer(driver)
            return Response(result_serializer.data)
        except Http404:
            return Response({'_app_notifications': [DRIVER_NOT_FOUND_ERROR]}, HTTP_400_BAD_REQUEST)
        except payment_method_service.ServiceError as pm_error:
            return Response({'_app_notifications': [pm_error.message]}, HTTP_400_BAD_REQUEST)
