# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib import auth
from django.core import exceptions

from idlecars import model_helpers, fields


class Driver(models.Model):
    auth_user = models.OneToOneField(auth.models.User, null=True) #TODO: null=False

    ssn = models.CharField(max_length=9, blank=True)
    documentation_approved = models.BooleanField(
        default=False,
        verbose_name='docs approved',
        db_column='documentation_complete'
    )

    sms_enabled = models.BooleanField(default=True)

    driver_license_image = model_helpers.StrippedCharField(
        max_length=300,
        blank=True,
    )
    fhv_license_image = model_helpers.StrippedCharField(
        max_length=300,
        blank=True,
        verbose_name="Hack License",
    )
    address_proof_image = model_helpers.StrippedCharField(
        max_length=300,
        blank=True,
        verbose_name="Motor Vehicle Record (MVR)",
    )
    no_mvr = models.BooleanField(default=False, verbose_name='Driver doesn\'t have an MVR')
    base_letter = model_helpers.StrippedCharField(max_length=300, blank=True)
    base_letter_rejected = models.BooleanField(default=False, verbose_name='base letter rejected')

    braintree_customer_id = models.CharField(max_length=32, null=True, blank=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.full_name()

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

    def app_credit(self):
        return self.auth_user.customer.app_credit

    def invite_code(self):
        return self.auth_user.customer.invite_code

    def all_docs_uploaded(self):
        return bool(
            self.driver_license_image and
            self.fhv_license_image and
            self.address_proof_image or self.no_mvr
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

        if self.base_letter and self.base_letter_rejected:
            raise exceptions.ValidationError(
                "Base letter should be either approved or rejected."
            )


    def save(self, *args, **kwargs):
        if self.pk is not None:
            import server.services.driver
            orig = Driver.objects.get(pk=self.pk)
            self = server.services.driver.pre_save(self, orig)
            super(Driver, self).save(*args, **kwargs)
        else:
            super(Driver, self).save(*args, **kwargs)
