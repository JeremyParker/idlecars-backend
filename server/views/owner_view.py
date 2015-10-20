# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from server import models
from server.serializers import OwnerSerializer
from server.permissions import OwnsOwner
from server.services import owner_service


class OwnerViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet
    ):
    model = models.Owner
    queryset = models.Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = (OwnsOwner,)

    def get_object(self):
        ''' override to map 'me' to the current user's driver object '''
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.request.user.is_authenticated() and self.kwargs[lookup_url_kwarg] == 'me':
            try:
                self.kwargs[lookup_url_kwarg] = models.Owner.objects.get(auth_users=self.request.user).pk
            except models.Owner.DoesNotExist:
                raise Http404
        return super(OwnerViewSet, self).get_object()

    @detail_route(methods=['post'], permission_classes=[OwnsOwner])
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
