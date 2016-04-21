# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from idlecars import model_helpers, fields
from server import models as server_models

'''
Removal represents an Owner's request to remove a driver from their medallion. Like Addition, it
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

    # TODO - hook this up to send an email
    # def save(self, *args, **kwargs):
    #     if self.pk is not None:
    #         orig = Driver.objects.get(pk=self.pk)
    #         self = server.services.removal.pre_save(self, orig)
    #         super(Driver, self).save(*args, **kwargs)
    #     else:
    #         super(Driver, self).save(*args, **kwargs)
