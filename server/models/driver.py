# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib import auth

from idlecars import model_helpers


class Driver(models.Model):
    auth_user = models.OneToOneField(auth.models.User, null=True) #TODO: null=False
    documentation_complete = models.BooleanField(default=False, verbose_name='docs confirmed')

    driver_license_image = model_helpers.StrippedCharField(max_length=100, blank=True)
    fhv_license_image = model_helpers.StrippedCharField(max_length=100, blank=True)
    address_proof_image = model_helpers.StrippedCharField(max_length=100, blank=True)
    defensive_cert_image = model_helpers.StrippedCharField(max_length=100, blank=True)

    def first_name(self):
        return self.auth_user.first_name

    def last_name(self):
        return self.auth_user.last_name

    def full_name(self):
        return self.auth_user.get_full_name()

    def phone_number(self):
        return self.auth_user.username

    def email(self):
        return self.auth_user.email

    def all_docs_uploaded(self):
        return (
            self.driver_license_image and
            self.fhv_license_image and
            self.address_proof_image and
            self.defensive_cert_image
            )
