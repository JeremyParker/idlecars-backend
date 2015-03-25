# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

from idlecars.constants import MAX_EMAIL_LENGTH
from idlecars import model_helpers

'''
Abstract base class for prospects - 
people who provide their email address through the landing page.
'''
class Prospect(models.Model):
    class Meta:
        abstract = True

    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        blank=False,
        unique=True,
        verbose_name='Email Address'
    )
    zipcode = models.CharField(
        max_length=5,
        blank=False,
        verbose_name='Zip Code',
        validators=[
            RegexValidator(
                r'^[0-9]+$',
                'Only numbers are allowed in a zip code.',
                'Invalid zip code'
            ),
            MinLengthValidator(5),
            MaxLengthValidator(5),
        ],
    )
    created_time = models.DateTimeField(auto_now_add=True)
    # TODO(JP):
    # referer_url = models.CharField(max_length=1000, null=True, blank=True)
    # device = model_helpers.ChoiceField(max_length=30, choices=DEVICES)
    # user_agent = 


class DriverProspect(Prospect):
    def __unicode__(self):
        return u"Driver: {email} {zipcode}".format(email=self.email, zipcode=self.zipcode)


class OwnerProspect(Prospect):
    def __unicode__(self):
        return u"Owner: {email} {zipcode}".format(email=self.email, zipcode=self.zipcode)


class DriverSurvey(models.Model):
    driver_prospect = models.ForeignKey(DriverProspect, null=True, related_name='driver_survey')
    source = models.CharField(max_length=32, verbose_name='How did you hear about idlecars?')
    other_source = models.CharField(max_length=255, blank=True, verbose_name='')


class OwnerSurvey(models.Model):
    owner_prospect = models.ForeignKey(OwnerProspect, null=True, related_name='owner_survey')
    source = models.CharField(max_length=32, verbose_name='How did you hear about idlecars?')
    other_source = models.CharField(max_length=255, blank=True, verbose_name='')
