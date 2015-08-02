# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib import auth
from django.core import exceptions

from idlecars import model_helpers, fields


class Driver(models.Model):
    auth_user = models.OneToOneField(auth.models.User, null=True) #TODO: null=False
    documentation_approved = models.BooleanField(
        default=False,
        verbose_name='docs approved',
        db_column='documentation_complete'
    )

    driver_license_image = model_helpers.StrippedCharField(max_length=300, blank=True)
    fhv_license_image = model_helpers.StrippedCharField(max_length=300, blank=True)
    address_proof_image = model_helpers.StrippedCharField(max_length=300, blank=True)
    defensive_cert_image = model_helpers.StrippedCharField(max_length=300, blank=True)

    notes = models.TextField(blank=True)

    def admin_display(self):
        return self.auth_user.get_full_name() or fields.format_phone_number(self.phone_number())

    def client_display(self):
        return self.auth_user.get_full_name() or 'New Driver'

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
        return bool(
            self.driver_license_image and
            self.fhv_license_image and
            self.address_proof_image and
            self.defensive_cert_image
        )

    def clean(self, *args, **kwargs):
        super(Driver, self).clean()

        if self.documentation_approved:
            if not self.all_docs_uploaded():
                raise exceptions.ValidationError(
                    "You can't mark docs approved until all documents are uploaded."
                )

            if not self.auth_user.first_name or not self.auth_user.last_name:
                raise exceptions.ValidationError(
                    "Please fill in the user's name and save, then set documentation approved."
                )

    def save(self, *args, **kwargs):
        import server.services.driver
        self = server.services.driver.pre_save(self)
        super(Driver, self).save(*args, **kwargs)
