# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0066_auto_20151002_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='incomplete_reason',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'Too Slow - another driver on our system booked the car'), (2, 'Owner Rejected - driver wasn\t approved'), (3, 'Driver Rejected - driver changed their mind'), (4, 'Missed - car rented out elsewhere before we found a driver'), (5, 'Test - a booking that one of us created as a test'), (6, 'Canceled - driver canceled the booking thru the app'), (7, 'Too Slow - insurance is too slow')]),
        ),
    ]
