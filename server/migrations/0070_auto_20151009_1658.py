# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0068_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='incomplete_reason',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'Too Slow - another driver on our system booked the car'), (2, "The Owner Rejected - driver wasn't approved. Don't know why yet."), (3, 'The Driver Rejected - at pickup'), (4, 'Missed - car rented out elsewhere before we found a driver'), (5, 'Test - a booking that one of us created as a test'), (6, 'Canceled - driver canceled thru the app before insurance approval'), (7, 'Driver Too Slow - driver did not submit their documents in time'), (8, 'Owner Too Slow - the insurance took too long'), (9, 'Driver rejected from insurance - too young'), (10, 'Driver rejected from insurance - experience'), (11, 'Driver rejected from insurance - points'), (12, 'No Base Letter - we cannot get a base letter'), (13, 'Some other reason - see notes field below')]),
        ),
    ]
