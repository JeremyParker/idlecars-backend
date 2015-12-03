# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import mandrill

from django.conf import settings
from django.http import HttpResponse, Http404

from rest_framework import viewsets, mixins, views, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from server.models import Driver
from services import password_reset_service, notification
from tests import sample_merge_vars
import serializers, models


class PasswordResetSetupView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.PasswordResetSetupSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone_number = serializer.validated_data['phone_number']
        password_reset = password_reset_service.create(phone_number)
        if password_reset:
            try:
                owner = password_reset.auth_user.owner_set.first()
                notification.send('owner_notifications.PasswordReset', password_reset)
            except Owner.DoesNotExist:
                driver = password_reset.auth_user.driver
                notification.send('driver_notifications.PasswordReset', password_reset)

            content = {'phone_number': phone_number}
            return Response(content, status=status.HTTP_201_CREATED)

        # Since this is AllowAny, don't give away the error.
        content = {'_app_notifications': [
            'Sorry, that didn\'t work. Please double-check your phone number.'
        ],}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.PasswordResetSerializer

    def patch(self, request, format=None):
        serializer = self.serializer_class(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.data['token']
        password = serializer.data['password']

        try:
            password_reset = models.PasswordReset.objects.get(token=token)
            # TODO - put this security feature back in as sson as owners can sign up more easily.
            # if password_reset.state != models.ConsumableToken.STATE_PENDING:
            #     # TODO(JP) - we should expire the token after a couple of hours
            #     # TODO(JP) - it'd be cool if we could just send them a new link here.
            #     content = {'_app_notifications': ['Sorry, this link doen\'t work any more.']}
            #     return Response(content, status=status.HTTP_400_BAD_REQUEST)

            user = password_reset.auth_user
            user.set_password(password)
            user.save()

            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)

            password_reset.state = models.ConsumableToken.STATE_CONSUMED
            password_reset.save()

            try:
                driver = password_reset.auth_user.driver
                notification.send('driver_notifications.PasswordResetConfirmation', password_reset)
            except Driver.DoesNotExist:
                notification.send('owner_notifications.PasswordResetConfirmation', password_reset)

            content = {'_app_notifications': [{'success': 'Your password has been set.'}], 'token': token.key}
            return Response(content, status=status.HTTP_200_OK)

        except models.PasswordReset.DoesNotExist:
            content = {'_app_notifications': ['Unable to verify user.']}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)


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
