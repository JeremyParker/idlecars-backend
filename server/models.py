# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

from idlecars import model_helpers

RATING = [
    (0, 'Terrible'),
    (1, 'Bad'),
    (2, 'Poor'),
    (3, 'OK'),
    (4, 'Good'),
    (5, 'Excellent'),
]

class Owner(models.Model):
    company_name = models.CharField(max_length=256, blank=True)
    address1 = models.CharField(blank=True, max_length=200)
    address2 = models.CharField(blank=True, max_length=200)
    city = models.CharField(blank=True, max_length=200)
    state_code = models.CharField(blank=True, max_length=2)
    zipcode = models.CharField(blank=True, max_length=5, verbose_name='Zip Code',
        validators=[
            RegexValidator(r'^[0-9]+$', 'Only numbers are allowed in a zip code.', 'Invalid zip'),
            MinLengthValidator(5),
            MaxLengthValidator(5),
        ],
    )
    split_shift = models.NullBooleanField(verbose_name="Accepts Split Shifts", blank=True)
    rating = models.IntegerField(
        choices=RATING,
        blank=True,
        null = True,
        help_text="Owner's rating based on previous experience."
    )
    last_engagement = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

    def name(self):
        if self.company_name:
            return self.company_name
        if self.user_account.count() == 1:
            return self.user_account.first().full_name()
        else:
            return None

    def __unicode__(self):
        name = self.name()
        return name or "Owner {}".format(self.pk)


class UserAccount(models.Model):
    first_name = model_helpers.StrippedCharField(max_length=30, blank=True)
    last_name = model_helpers.StrippedCharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=40, blank=True)
    email = models.CharField(blank=True, max_length=128, unique=True, null=True)

    # if this user is an owner, they have an owner profile
    owner = models.ForeignKey(Owner, blank=True, null=True, related_name="user_account")

    def full_name(self):
        return u"{first} {last}".format(first=self.first_name, last=self.last_name)

    def __unicode__(self):
        return "{name} ({contact})".format(
            name=self.full_name(),
            contact=self.email or self.phone_number or 'no contact')


class Car(models.Model):
    STATUS = model_helpers.Choices(available='Available', unknown='Unknown', busy='Busy')
    status = model_helpers.ChoiceField(choices=STATUS, max_length=32, default='Unknown')
    status_date = models.DateField(blank=True, null=True)

    make = models.CharField(max_length=128, blank=True)
    model = models.CharField(max_length=128, blank=True)
    YEARS = [(y, unicode(y)) for y in range(1995, (datetime.datetime.now().year+1))]
    year = models.IntegerField(choices=YEARS, max_length=4, blank=True, null=True)
    solo_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    solo_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    split_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    split_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    MIN_LEASE_CHOICES = model_helpers.Choices(
        _0_no_min='No Minimum',
        _1_one_week='One Week',
        _2_two_weeks='Two Weeks',
        _3_three_weeks='Three Weeks',
        _4_one_month='One Month',
        _5_six_weeks='Six Weeks',
        _6_two_months='Two Months',
    )
    min_lease = model_helpers.ChoiceField(
        choices=MIN_LEASE_CHOICES,
        max_length=32,
        default="No Minimum"
    )
    notes = models.TextField(blank=True)
