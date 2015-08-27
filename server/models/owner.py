# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from operator import attrgetter

from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.validators import MaxLengthValidator
from django.contrib.auth.models import User as AuthUser


class Owner(models.Model):
    auth_user = models.ManyToManyField(AuthUser)
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
    RATING = [
        (0, 'Terrible'),
        (1, 'Bad'),
        (2, 'Poor'),
        (3, 'OK'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    rating = models.IntegerField(
        choices=RATING,
        blank=True,
        null = True,
        help_text="Owner's rating based on previous experience."
    )
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
