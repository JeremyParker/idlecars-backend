# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from decimal import Decimal, ROUND_UP

from django.db import models
from django.utils import timezone

from idlecars import model_helpers

from . import Owner, MakeModel, Insurance


class Car(models.Model):
    owner = models.ForeignKey(Owner, blank=True, null=True, related_name='cars')

    STATUS_AVAILABLE = 'available'
    STATUS_UNKNOWN = 'unknown'
    STATUS_BUSY = 'busy'
    STATUS = model_helpers.Choices(available='Available', unknown='Unknown', busy='Busy')
    status = model_helpers.ChoiceField(choices=STATUS, max_length=32, default='Unknown')

    next_available_date = models.DateField(blank=True, null=True)
    last_status_update = models.DateTimeField()
    make_model = models.ForeignKey(
        MakeModel,
        verbose_name="Make & Model",
        null=False,
        default=1,
    )
    hybrid = models.BooleanField(default=False, null=False, verbose_name="This car is a hybrid")
    YEARS = [(y, unicode(y)) for y in range((timezone.now().year+1), 1995, -1)]
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
        _02_one_week='7 days',
        _03_two_weeks='14 days',
        _04_three_weeks='21 days',
        _05_one_month='30 days',
        _06_six_weeks='45 days',
        _07_two_months='60 days',
        _08_three_months='90 days',
        _09_four_months='120 days',
        _10_five_months='150 days',
        _11_six_months='180 days',
    )
    min_lease = model_helpers.ChoiceField(
        choices=MIN_LEASE_CHOICES,
        max_length=32,
        default='_00_unknown',
    )

    def minimum_rental_days(self):
        return {
            '_00_unknown': None,
            '_01_no_min': 1,
            '_02_one_week': 7,
            '_03_two_weeks': 14,
            '_04_three_weeks': 21,
            '_05_one_month': 30,
            '_06_six_weeks': 42,
            '_07_two_months': 60,
            '_08_three_months': 90,
            '_09_four_months': 120,
            '_10_five_months': 150,
            '_11_six_months': 180,
        }[self.min_lease]

    notes = models.TextField(blank=True)
    created_time = models.DateTimeField(auto_now_add=True, null=True)

    COLOR_BLACK = 0
    COLOR_CHARCOAL = 1
    COLOR_GREY = 2
    COLOR_DARK_BLUE = 3
    COLOR_BLUE = 4
    COLOR_TAN = 5
    COLOR_WHITE = 6

    COLOR_CHOICES = [
        (COLOR_BLACK, 'Black'),
        (COLOR_CHARCOAL, 'Charcoal'),
        (COLOR_GREY, 'Grey'),
        (COLOR_DARK_BLUE, 'Dark Blue'),
        (COLOR_BLUE, 'Blue'),
        (COLOR_TAN, 'Tan'),
        (COLOR_WHITE, 'White'),
    ]
    exterior_color = models.IntegerField(
        choices=COLOR_CHOICES,
        blank=True,
        null=True,
    )
    interior_color = models.IntegerField(
        choices=COLOR_CHOICES,
        blank=True,
        null=True,
    )
    last_known_mileage = models.IntegerField(blank=True, null=True)
    last_mileage_update = models.DateTimeField(blank=True, null=True)
    insurance = models.ForeignKey(Insurance, blank=True, null=True)

    def display_mileage(self):
        # TODO(JP): have this change with time based on past data?
        if self.last_known_mileage:
            return '{},000'.format(self.last_known_mileage / 1000)
        else:
            return None

    def effective_status(self):
        if self.next_available_date and self.next_available_date < timezone.now().date():
            return 'Available'
        else:
            return self.status

    # TODO: remove this once the client shows cents in the listing price.
    def normalized_cost(self):
        return int((self.solo_cost + 6) / 7)

    def quantized_cost(self):
        return (self.solo_cost / Decimal(7.00)).quantize(Decimal('.01'), rounding=ROUND_UP)

    def __unicode__(self):
        if self.plate and self.year:
            return '{} {} ({})'.format(self.year, self.make_model, self.plate)
        elif self.plate:
            return 'Unkown Car ({})'.format(self.plate)
        elif self.make_model:
            return unicode(self.make_model)
        else:
            return '{}'.format(self.pk)

    def display_name(self):
        if self.year:
            return '{} {}'.format(self.year, self.make_model)
        else:
            return unicode(self.make_model)

    def save(self, *args, **kwargs):
        if self.pk is None:
            if not self.last_status_update:
                self.last_status_update = timezone.now()
        else:
            orig = Car.objects.get(pk=self.pk)  # TODO(JP): maybe use __class__ to be more flexible
            if orig.status != self.status:
                self.last_status_update = timezone.now()
            if orig.last_known_mileage != self.last_known_mileage:
                self.last_mileage_update = timezone.now()

        super(Car, self).save(*args, **kwargs)
