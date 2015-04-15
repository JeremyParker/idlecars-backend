# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response

import models
import serializers


@api_view(('GET',))
def api_root(request, format=None):
    import pdb; pdb.set_trace()
    return Response({
        'cars': reverse('car-list', request=request, format=format),
    })


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Car.objects.all()
    serializer_class = serializers.CarSerializer
