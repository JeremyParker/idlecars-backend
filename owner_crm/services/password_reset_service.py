# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import auth

from owner_crm import models
from owner_crm.services import notification


def create(phone_number):
    try:
        auth_user = auth.models.User.objects.get(username=phone_number)
        if auth_user.is_active:
            pending_resets = models.PasswordReset.objects.filter(auth_user=auth_user)
            pending_resets.filter(
                state=models.ConsumableToken.STATE_PENDING
            ).update(
                state=models.ConsumableToken.STATE_RETRACTED
            )
            return models.PasswordReset.objects.create(auth_user=auth_user)
    except auth.models.User.DoesNotExist:
        pass
    return None


def invite_owner(auth_user):
    password_reset = create(auth_user.username)
    if password_reset:
        notification.send('owner_notifications.AccountCreated', password_reset)
