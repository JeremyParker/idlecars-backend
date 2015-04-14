# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from operator import attrgetter

from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.validators import MaxLengthValidator, EmailValidator

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
        names = sorted(self.user_account.all(), key=attrgetter('last_name'))
        return ', '.join([u.full_name() for u in names])

    # get a value from the associated UserAccount, or return null, or 'multiple values'
    def get_user_account_attr(self, attrib):
        users = self.user_account.all()
        if not users:
            return ''
        elif users.count() == 1:
            return getattr(self.user_account.get(), attrib)
        else:
            return 'multiple values'

    def number(self):
        return self.get_user_account_attr('phone_number')

    def email(self):
        return self.get_user_account_attr('email')

    def __unicode__(self):
        name = self.name()
        return name or "Owner {}".format(self.pk)


class UserAccount(models.Model):
    first_name = model_helpers.StrippedCharField(max_length=30, blank=True)
    last_name = model_helpers.StrippedCharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=40, blank=True)
    email = models.CharField(
        blank=True,
        max_length=128,
        unique=True,
        null=True,
        validators=[EmailValidator()],
    )

    # if this user is an owner, they have an owner profile
    owner = models.ForeignKey(Owner, blank=True, null=True, related_name="user_account")

    def clean(self, *args, **kwargs):
        self.email = self.email.lower().strip() or None
        super(UserAccount, self).clean(*args, **kwargs)

    def full_name(self):
        return ' '.join([n for n in [self.first_name, self.last_name] if n])

    def __unicode__(self):
        return "{name} ({contact})".format(
            name=self.full_name(),
            contact=self.email or self.phone_number or 'no contact')


class MakeModel(models.Model):
    make = models.CharField(max_length=128, blank=True)
    model = models.CharField(max_length=128, blank=True)
    def __unicode__(self):
        return '{} {}'.format(self.make, self.model)


class Car(models.Model):
    owner = models.ForeignKey(Owner, blank=True, null=True, related_name='cars')
    STATUS = model_helpers.Choices(available='Available', unknown='Unknown', busy='Busy')
    status = model_helpers.ChoiceField(choices=STATUS, max_length=32, default='Unknown')
    next_available_date = models.DateField(blank=True, null=True)
    make_model = models.ForeignKey(
        MakeModel,
        related_name='+',
        verbose_name="Make & Model",
        blank=True,
        null=True
    )
    YEARS = [(y, unicode(y)) for y in range((datetime.datetime.now().year+1), 1995, -1)]
    year = models.IntegerField(choices=YEARS, max_length=4, blank=True, null=True)
    plate = models.CharField(max_length=24, blank=True)
    solo_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    solo_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    split_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    split_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    MIN_LEASE_CHOICES = model_helpers.Choices(
        _0_unknown='Unknown',
        _1_no_min='No Minimum',
        _2_one_week='One Week',
        _3_two_weeks='Two Weeks',
        _4_three_weeks='Three Weeks',
        _5_one_month='One Month',
        _6_six_weeks='Six Weeks',
        _7_two_months='Two Months',
    )
    min_lease = model_helpers.ChoiceField(
        choices=MIN_LEASE_CHOICES,
        max_length=32,
        default='No Minimum'
    )
    notes = models.TextField(blank=True)

    def effective_status(self):
        if self.next_available_date and self.next_available_date < datetime.date.today():
            return 'Available'
        else:
            return self.status

    def __unicode__(self):
        if self.year:
            return '{} {}'.format(self.year, self.make_model)
        else:
            return unicode(self.make_model)
