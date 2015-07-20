# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import auth
from django.db import models

from consumable_token import ConsumableToken


class PasswordReset(ConsumableToken):
    auth_user = models.ForeignKey(auth.models.User)
