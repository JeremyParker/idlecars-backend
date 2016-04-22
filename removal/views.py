# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from server import models as server_models

from removal.serializers import RemovalSerializer
from removal.models import Removal
from removal.permissions import OwnsRemoval


class RemovalViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):
    serializer_class = RemovalSerializer
    model = Removal

    def get_permissions(self):
        # TODO - don't allow non-authenticated user to create an Removal
        return (IsAuthenticated() if self.request.method == 'POST' else OwnsRemoval()),

    def get_queryset(self):
        owner = self.request.user.owner_set.first()
        if self.action == 'list':
            return Removal.objects.filter(owner=owner)
        return Removal.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            return super(RemovalViewSet, self).update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'_app_notifications': [e.detail]}, status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        owner = server_models.Owner.objects.get(auth_users=self.request.user)
        serializer.save(owner=owner)
