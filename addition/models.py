# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from idlecars import email
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
            self.first_name and
            self.last_name and
            self.ssn and
            self.driver_license_image and
            self.fhv_license_image and
            (self.address_proof_image or self.mvr_authorized)
        )

    def save(self, *args, **kwargs):
        if self.pk is None:
            return super(Addition, self).save(*args, **kwargs)

        if self.complete() and not Addition.objects.get(pk=self.pk).complete():

            # send an email to the owner who made the request
            email.send_async(
                template_name='no_button_no_image',
                subject='Your request to add {} {} has been sent successfully.'.format(
                    self.first_name,
                    self.last_name,
                ),
                merge_vars={
                    self.owner.auth_users.first().email: {
                        'FNAME': self.owner.name(),
                        'HEADLINE': 'Your request to add a driver has been sent.',
                        'TEXT': '''
                            All Taxi has received your request to add {} {}.
                            You will be notified when your driver has been added.
                            '''.format(
                                self.first_name,
                                self.last_name,
                        ),
                    }
                },
            )

            #send an email to ops
            email.send_async(
                template_name='one_button_two_images',
                subject='{} wants to add {} {}'.format(
                    self.owner.name(),
                    self.first_name,
                    self.last_name,
                ),
                merge_vars=self.merge_vars_ops()
            )

        super(Addition, self).save(*args, **kwargs)

    def merge_vars_ops(self):
            if self.address_proof_image:
                mvr_text = '<a href="{}">(click here to download)</a>'.format(self.address_proof_image)
            else:
                mvr_text = 'we are Authorized to run the MVR'

            return {
                settings.OPS_EMAIL: {
                    'PREVIEW': '{} wants to add a driver.'.format(self.owner.name()),
                    'FNAME': 'operations team',
                    'HEADLINE': '{} wants to add a driver.'.format(self.owner.name()),
                    'TEXT0': '''
                    Owner Info:
                    <ul>
                        <li>Name: {owner_name}</li>
                        <li>Email: {owner_email}</li>
                        <li>Phone: {owner_phone}</li>
                        <li>Medallion: {plate}</li>
                        <li>Last 4 of SSN: {owner_ssn}</li>
                    </ul>

                    Driver Info:
                    <ul>
                        <li>Name: {driver_first} {driver_last}</li>
                        <li>phone number: {driver_phone}</li>
                        <li>email address: {driver_email}</li>
                        <li>Social Security Number: {driver_ssn}</li>
                        <li>MVR: {mvr_text}</li>
                    </ul>
                    '''.format(
                        owner_name=self.owner.name(),
                        owner_email=self.owner.auth_users.first().email,
                        owner_phone=self.owner.auth_users.first().username,
                        plate=self.plate,
                        owner_ssn=self.owner.social,

                        driver_first=self.first_name,
                        driver_last=self.last_name,
                        driver_phone=self.phone_number,
                        driver_email=self.email,
                        driver_ssn=self.ssn,
                        mvr_text=mvr_text
                    ),
                    'IMAGE_1_URL': self.driver_license_image,
                    'TEXT1': 'Drivers License <a href="{}">click here to download</a>'.format(self.driver_license_image),
                    'IMAGE_2_URL': self.fhv_license_image,
                    'TEXT2': 'Hack License <a href="{}">click here to download</a>'.format(self.fhv_license_image),
                    'TEXT5': 'Check the admin tool for more details or to edit this request',
                    'CTA_LABEL': 'Edit Driver Add Request',
                    'CTA_URL': 'http://alltaxi.herokuapp.com{}'.format(
                        reverse('admin:addition_addition_change', args=(self.pk,))
                    ),
                }
            }
