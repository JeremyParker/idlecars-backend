# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

from idlecars.constants import MAX_EMAIL_LENGTH
from idlecars import model_helpers


ROLE_CHOICES = model_helpers.Choices(
    driver='I want to drive.',
    owner='I own a car.',
)

SOURCE_CHOICES = model_helpers.Choices(
    _2_mouth='Word of mouth',
    _3_poster='I saw a poster',
    _4_search='I searched online',
    _5_facebook='Facebook',
    _6_twitter='Twitter',
    _7_other="Other"
)

EXCHANGE_CHOICES = model_helpers.Choices(
    _no_response='No response',
    garage='I can pick up the vehicle from a parking garage at the start of every shift.',
    delivery='I would need the vehicle delivered to my home at the start of every shift',
    overnight='I would need to keep the vehicle in my posession between shifts'
)

VEHICLE_CHOICES = model_helpers.Choices(
    suv='Luxury SUV',
    sedan='Luxury Sedan',
    uber_x='Any Vehicle'
)

'''
Class for contacts.
People who provide their email address through the landing page.
'''
class Contact(models.Model):
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
    role = model_helpers.ChoiceField(choices=ROLE_CHOICES, max_length=16, default='Driver')
    created_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"{role}: {email}".format(role=self.role, email=self.email)
    # TODO(JP):
    # referer_url = models.CharField(max_length=1000, null=True, blank=True)
    # device = model_helpers.ChoiceField(max_length=30, choices=DEVICES)
    # user_agent =


class DriverSurvey(models.Model):
    contact = models.ForeignKey(Contact, null=True, related_name='driver_survey')
    source = model_helpers.ChoiceField(
        choices=sorted(SOURCE_CHOICES, key=lambda x: x[0]),
        max_length=32,
        blank=True,
        verbose_name='How did you hear about idlecars?',
    )
    other_source = models.CharField(max_length=255, blank=True, verbose_name='')
    licenced = models.BooleanField(default=False, verbose_name='I have a commercial driver\'s license')
    credit_card = models.BooleanField(default=False, verbose_name='I have a credit card')
    car_owner = models.BooleanField(default=False, verbose_name='I own a car')

    account_uber = models.BooleanField(default=False, verbose_name='Uber')
    account_lyft = models.BooleanField(default=False, verbose_name='Lyft')
    account_whisk = models.BooleanField(default=False, verbose_name='Whisk')
    account_via = models.BooleanField(default=False, verbose_name='Via')
    account_gett = models.BooleanField(default=False, verbose_name='Gett')
    account_other = models.BooleanField(default=False, verbose_name='Other Dispatcher')
    account_other_name = models.CharField(max_length=255, blank=True, verbose_name='')

    exchange = model_helpers.ChoiceField(
        choices=sorted(EXCHANGE_CHOICES, key=lambda x: x[0]),
        max_length=256,
        default=EXCHANGE_CHOICES['_no_response'],
        verbose_name='',
    )
    vehicle_type = model_helpers.ChoiceField(
        choices=VEHICLE_CHOICES,
        max_length=64,
        blank=True,
        verbose_name='What kind of vehicle would you prefer to rent?',
    )

    midnight = datetime.time(0)

    rent_monday =       models.BooleanField(default=False, verbose_name='Monday')
    rent_tuesday =      models.BooleanField(default=False, verbose_name='Tuesday')
    rent_wednesday =    models.BooleanField(default=False, verbose_name='Wednesday')
    rent_thursday =     models.BooleanField(default=False, verbose_name='Thursday')
    rent_friday =       models.BooleanField(default=False, verbose_name='Friday')
    rent_saturday =     models.BooleanField(default=False, verbose_name='Saturday')
    rent_sunday =       models.BooleanField(default=False, verbose_name='Sunday')

    start_monday =       models.TimeField(default=midnight, verbose_name='')
    start_tuesday =      models.TimeField(default=midnight, verbose_name='')
    start_wednesday =    models.TimeField(default=midnight, verbose_name='')
    start_thursday =     models.TimeField(default=midnight, verbose_name='')
    start_friday =       models.TimeField(default=midnight, verbose_name='')
    start_saturday =     models.TimeField(default=midnight, verbose_name='')
    start_sunday =       models.TimeField(default=midnight, verbose_name='')

    end_monday =       models.TimeField(default=midnight, verbose_name='')
    end_tuesday =      models.TimeField(default=midnight, verbose_name='')
    end_wednesday =    models.TimeField(default=midnight, verbose_name='')
    end_thursday =     models.TimeField(default=midnight, verbose_name='')
    end_friday =       models.TimeField(default=midnight, verbose_name='')
    end_saturday =     models.TimeField(default=midnight, verbose_name='')
    end_sunday =       models.TimeField(default=midnight, verbose_name='')


class OwnerSurvey(models.Model):
    contact = models.ForeignKey(Contact, null=True, related_name='owner_survey')
    source = model_helpers.ChoiceField(
        choices=SOURCE_CHOICES,
        max_length=32,
        blank=True,
        verbose_name='How did you hear about idlecars?',
    )
    other_source = models.CharField(max_length=255, blank=True, verbose_name='')
