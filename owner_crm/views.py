# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import mandrill

from django.contrib import auth
from django.conf import settings
from django.http import HttpResponse, Http404

from rest_framework import viewsets, mixins, views, permissions
from rest_framework.response import Response
from rest_framework import status

from services import driver_emails
from tests import sample_merge_vars
import serializers, models


class PasswordResetSetups(views.APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.PasswordResetSetupSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.DATA)

        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            try:
                auth_user = auth.models.User.objects.get(username=phone_number)
                if auth_user.is_active:
                    password_reset = models.PasswordReset.objects.create(auth_user=auth_user)
                    driver_emails.password_reset(password_reset)
                    content = {'phone_number': phone_number}
                    return Response(content, status=status.HTTP_201_CREATED)

            except auth.models.User.DoesNotExist:
                pass

            # Since this is AllowAny, don't give away error.
            content = {'detail': 'Password reset not allowed.'}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetExecutions(views.APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.PasswordResetExecutionSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.DATA)

        if serializer.is_valid():
            token = serializer.data['token']
            password = serializer.data['password']

            try:
                password_reset = PasswordResetCode.objects.get(token=token)
                password_reset.auth_user.set_password(password)
                password_reset.auth_user.save()
                password_reset.state = STATE_CONSUMED
                content = {'success': 'Password reset.'}
                return Response(content, status=status.HTTP_200_OK)
            except PasswordResetCode.DoesNotExist:
                content = {'detail': 'Unable to verify user.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class UpdateRenewalView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.Renewal.objects.all()
    serializer_class = serializers.Renewal
    lookup_field = 'token'


def email_preview(request, pk):
    if not pk in sample_merge_vars.merge_vars:
        raise Http404('That email template doesn\'t exist.')

    client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
    merge_vars = sample_merge_vars.merge_vars[pk]

    # format the merge_vars for this API call
    pairs = merge_vars[merge_vars.keys()[0]]
    template_content = [{"name": k, "content": v} for k, v in pairs.iteritems()]
    rendered = client.templates.render(pk, [], merge_vars=template_content)
    return HttpResponse(rendered['html'])
