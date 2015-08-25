# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from server import models
from server.services import payment_method as payment_method_service
from server.serializers import DriverSerializer, NonceSerializer
from server.permissions import OwnsDriver


class DriverViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):
    serializer_class = DriverSerializer
    model = models.Driver
    queryset = models.Driver.objects.all()

    def get_permissions(self):
        # allow non-authenticated user to create a Driver
        return (AllowAny() if self.request.method == 'POST' else OwnsDriver()),

    def get_object(self):
        ''' override to map 'me' to the current user's driver object '''
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.request.user.is_authenticated() and self.kwargs[lookup_url_kwarg] == 'me':
            self.kwargs[lookup_url_kwarg] = models.Driver.objects.get(auth_user=self.request.user).pk
        return super(DriverViewSet, self).get_object()

    @detail_route(methods=['post'], permission_classes=[OwnsDriver])
    def payment_method(self, request, pk=None):
        serializer = NonceSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        driver = self.get_object()
        nonce = serializer.validated_data['nonce']
        driver = payment_method_service.add_payment_method(driver, nonce)
        result_serializer = self.get_serializer(driver)
        return Response(result_serializer.data)
