# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated

from server import models
from server.serializers import OwnerSerializer
from server.permissions import OwnsOwner
from server.services import owner_service


class OwnerViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):
    serializer_class = OwnerSerializer
    model = models.Owner
    queryset = models.Owner.objects.all()

    def get_permissions(self):
        # special case for create: you just have to be authenticated.
        if self.request.method == 'POST' and self.action == 'create':
            return (IsAuthenticated(),)
        return (OwnsOwner()),

    def get_object(self):
        ''' override to map 'me' to the current user's owner object '''
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.request.user.is_authenticated() and self.kwargs[lookup_url_kwarg] == 'me':
            try:
                me_pk = models.Owner.objects.get(auth_users=self.request.user).pk
                self.kwargs[lookup_url_kwarg] = me_pk
            except models.Owner.DoesNotExist:
                new_owner = owner_service.create(auth_user=self.request.user)
                return new_owner

        return super(OwnerViewSet, self).get_object()

    def perform_create(self, serializer):
        user = self.request.user
        try:
            owner = models.Owner.objects.get(auth_users=user)
        except models.Owner.DoesNotExist:
            owner = owner_service.create(auth_user=user)
        serializer.instance = owner

    @detail_route(methods=['post'])
    def bank_link(self, request, pk=None):
        owner = self.get_object()
        error_fields, error_msg = owner_service.link_bank_account(owner, request.data)

        if not error_msg:
            return Response({}, status=status.HTTP_201_CREATED)
        else:
            data = {
                'error_fields': error_fields,
                '_app_notifications': error_msg
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
