# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from idlecars import model_helpers


class Driver(models.Model):
    documentation_complete = models.BooleanField(default=False, verbose_name='docs confirmed')

    driver_license_image = model_helpers.StrippedCharField(max_length=100, blank=True)
    fhv_license_image = model_helpers.StrippedCharField(max_length=100, blank=True)
    address_proof_image = model_helpers.StrippedCharField(max_length=100, blank=True)
    defensive_cert_image = model_helpers.StrippedCharField(max_length=100, blank=True)

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
