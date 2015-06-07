# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from . import UserAccount


class Driver(models.Model):
    user_account = models.OneToOneField(UserAccount, primary_key=True)
    documentation_complete = models.BooleanField(default=False, verbose_name='docs confirmed')

    def first_name(self):
        return self.user_account.first_name()

    def last_name(self):
        return self.user_account.last_name()

    def full_name(self):
        return self.user_account.full_name()

    def phone_number(self):
        return self.user_account.phone_number

    def email(self):
        return self.user_account.email
