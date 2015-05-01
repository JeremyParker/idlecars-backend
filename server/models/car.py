# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models

from idlecars import model_helpers

from .owner import Owner
from .make_model import MakeModel


class Car(models.Model):
    owner = models.ForeignKey(Owner, blank=True, null=True, related_name='cars')

    STATUS = model_helpers.Choices(available='Available', unknown='Unknown', busy='Busy')
    STATUS_AVAILABLE = 'available'
    STATUS_UNKNOWN = 'unknown'
    STATUS_BUSY = 'busy'

    status = model_helpers.ChoiceField(choices=STATUS, max_length=32, default='Unknown')
    next_available_date = models.DateField(blank=True, null=True)
    make_model = models.ForeignKey(
        MakeModel,
        related_name='+',
        verbose_name="Make & Model",
        blank=True,
        null=True
    )
    hybrid = models.BooleanField(default=False, null=False, verbose_name="This car is a hybrid")
    YEARS = [(y, unicode(y)) for y in range((datetime.datetime.now().year+1), 1995, -1)]
    year = models.IntegerField(choices=YEARS, blank=True, null=True)
    plate = models.CharField(max_length=24, blank=True)
    base = models.CharField(max_length=64, blank=True)
    solo_cost = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    solo_deposit = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    split_cost = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    split_deposit = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)

    MIN_LEASE_CHOICES = model_helpers.Choices(
        _00_unknown='Unknown',
        _01_no_min='No',
        _02_one_week='One Week',
        _03_two_weeks='Two Weeks',
        _04_three_weeks='Three Weeks',
        _05_one_month='One Month',
        _06_six_weeks='Six Weeks',
        _07_two_months='Two Months',
        _08_three_months='Three Months',
        _09_four_months='Four Months',
        _10_five_months='Five Months',
        _11_six_months='Six Months',
    )
    min_lease = model_helpers.ChoiceField(
        choices=MIN_LEASE_CHOICES,
        max_length=32,
        default='_00_unknown',
    )
    notes = models.TextField(blank=True)
    created_time = models.DateTimeField(auto_now_add=True, null=True)

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
