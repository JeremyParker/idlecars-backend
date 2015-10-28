# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


class ICCreateModelMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        try:
            return super(ICCreateModelMixin, self).create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
