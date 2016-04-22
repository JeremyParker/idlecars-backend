# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from server import models as server_models

from addition.serializers import AdditionSerializer
from addition.models import Addition
from addition.permissions import OwnsAddition


class AdditionViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):
    serializer_class = AdditionSerializer
    model = Addition

    def get_permissions(self):
        # TODO - don't allow non-authenticated user to create an Addition
        return (IsAuthenticated() if self.request.method == 'POST' else OwnsAddition()),

    def get_queryset(self):
        owner = self.request.user.owner_set.first()
        if self.action == 'list':
            return Addition.objects.filter(owner=owner)
        return Addition.objects.all()

    def update(self, request, *args, **kwargs):
        if 'mvr_authorized' in request.data:
            addition = self.get_object()
            addition.mvr_authorized=timezone.now()
            addition.save()

        try:
            return super(AdditionViewSet, self).update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'_app_notifications': [e.detail]}, status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        owner = server_models.Owner.objects.get(auth_users=self.request.user)
        serializer.save(owner=owner)
