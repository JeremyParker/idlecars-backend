# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0034_auto_20150627_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='driver',
            name='documentation_complete',
        ),
        migrations.AddField(
            model_name='driver',
            name='documentation_approved',
            field=models.BooleanField(default=False, verbose_name='docs approved', db_column='documentation_complete'),
        ),
        migrations.AlterField(
            model_name='booking',
            name='state',
            field=models.IntegerField(default=1, choices=[(1, 'Pending - waiting for driver docs'), (2, 'Complete - checking driver creds'), (3, 'Requested - waiting for owner/insurance'), (4, 'Accepted - waiting for deposit, ssn, contract'), (5, 'Booked - car marked busy with new available_time'), (6, "Flake - Didn't Submit Docs in 24 hours"), (7, 'Too Slow - somebody else booked your car'), (8, 'Owner Rejected - driver wasn\t approved'), (9, 'Driver Rejected - driver changed their mind'), (10, 'Missed - car rented out before we found a driver'), (11, 'Test - a booking that one of us created as a test'), (12, 'Canceled - driver canceled the booking thru the app')]),
        ),
    ]
