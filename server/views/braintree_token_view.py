# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from server.payment_gateways import braintree_payments
from server.models import Driver


class BraintreeTokenView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        data = braintree_payments.initialize_gateway()
        return Response(data, status=status.HTTP_200_OK)
