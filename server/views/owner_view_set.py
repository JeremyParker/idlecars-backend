# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from server.models import Owner
from server.services import owner_bank_link_service
from server.permissions import OwnsOwner


class OwnerViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet
    ):
    queryset = Owner.objects.all()

    @detail_route(methods=['post'], permission_classes=[OwnsOwner])
    def bank_link(self, request, pk=None):
        owner = self.get_object()
        owner_bank_link_service.link(owner, request.data)
        return Response({})
