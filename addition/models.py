# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from idlecars import model_helpers, fields
from server import models as server_models

'''
Addition represents a request that an owner makes to add a driver to one of their cars. This
does NOT create a Driver account, and has nothing to do with existing Driver instances.
'''
class Addition(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey(server_models.Owner, blank=True, null=True, related_name='additions')
    plate = models.CharField(max_length=24, blank=True, verbose_name="Medallion")

    phone_number = models.CharField(max_length=40, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    ssn = models.CharField(max_length=9, blank=True)

    # Did the owner authorize All Taxi to run an MVR for this driver?
    mvr_authorized = models.DateTimeField(null=True, blank=True)

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
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.get_full_name()

    def admin_display(self):
        return self.get_full_name() or fields.format_phone_number(self.phone_number())

    def client_display(self):
        return self.get_full_name() or 'New Driver'

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def complete(self):
        return bool(
            self.phone_number and
            self.email and
            self.first_name and
            self.last_name and
            self.driver_license_image and
            self.fhv_license_image and
            (self.address_proof_image or self.mvr_authorized)
        )

    # TODO - hook this up to send an email
    # def save(self, *args, **kwargs):
    #     if self.pk is not None:
    #         orig = Driver.objects.get(pk=self.pk)
    #         self = server.services.addition.pre_save(self, orig)
    #         super(Driver, self).save(*args, **kwargs)
    #     else:
    #         super(Driver, self).save(*args, **kwargs)
