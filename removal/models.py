# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf import settings

from idlecars import model_helpers, fields, email
from server import models as server_models

'''
Removal represents an Owner's request to remove a driver from their medallion. Like Removal, it
has nothing to do with existing Driver instances.
'''
class Removal(models.Model):
    created_time = models.DateTimeField(auto_now_add=True, blank=True)

    owner = models.ForeignKey(server_models.Owner, blank=True, null=True, related_name='removals')

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    hack_license_number = models.CharField(_('hack_license_number'), max_length=7, blank=True)

    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.get_full_name()

    def admin_display(self):
        return self.get_full_name() or self.hack_license_number

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def complete(self):
        return bool(
            self.first_name and
            self.last_name and
            self.hack_license_number
        )

    def save(self, *args, **kwargs):
        if self.pk is  None:
            return super(Removal, self).save(*args, **kwargs)

        if self.complete() and not Removal.objects.get(pk=self.pk).complete():

            # send an email to the owner who made the request
            email.send_async(
                template_name='no_button_no_image',
                subject='Your request to remove {} {} has been sent successfully.'.format(
                    self.first_name,
                    self.last_name,
                ),
                merge_vars={
                    self.owner.auth_users.first().email: {
                        'FNAME': self.owner.name(),
                        'HEADLINE': 'Your request to remove a driver has been sent.',
                        'TEXT': '''
                            All Taxi has received your request to remove {} {}.
                            You will be notified when your driver has been removed.
                            '''.format(
                                self.first_name,
                                self.last_name,
                        ),
                    }
                },
            )

            #send an email to ops
            email.send_async(
                template_name='one_button_no_image',
                subject='{} wants to remove {} {}'.format(
                    self.owner.name(),
                    self.first_name,
                    self.last_name,
                ),
                merge_vars=self.merge_vars_ops()
            )

        super(Removal, self).save(*args, **kwargs)

    def merge_vars_ops(self):
            return {
                settings.OPS_EMAIL: {
                    'FNAME': 'operations team',
                    'HEADLINE': '{} wants to remove a driver.'.format(self.owner.name()),
                    'TEXT': '''
                    <ul>
                    <li>Driver Name: {} {}</li>
                    <li>Hack License Number: {}</li>
                    </ul>
                    Check the admin tool for more details or to edit this request.
                    '''.format(
                        self.first_name,
                        self.last_name,
                        self.hack_license_number,
                    ),
                    'CTA_LABEL': 'Driver Removal',
                    'CTA_URL': reverse('admin:removal_removal_change', args=(self.pk,)),
                }
            }
