# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from . import UserAccount


class Driver(models.Model):
    user_account = models.OneToOneField(UserAccount, primary_key=True)
    documentation_complete = models.BooleanField(default=False)
