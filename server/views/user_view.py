# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.contrib import auth

from rest_framework.serializers import ValidationError
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from server.serializers import UserSerializer, UserCreateSerializer
from server.permissions import OwnsUser


User = auth.get_user_model()


class UserViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet,
    ):
    model = User
    queryset = User.objects.all().select_related('driver')
    permission_classes = (OwnsUser,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_object(self):
        ''' override to map 'me' to the current user's User object '''
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.request.user.is_authenticated() and self.kwargs[lookup_url_kwarg] == 'me':
            try:
                self.kwargs[lookup_url_kwarg] = self.request.user.pk
            except User.DoesNotExist:
                raise Http404
        return super(UserViewSet, self).get_object()

    def update(self, request, *args, **kwargs):
        try:
            return super(UserViewSet, self).update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'_app_notifications': e.detail.values()[0]}, status.HTTP_400_BAD_REQUEST)
