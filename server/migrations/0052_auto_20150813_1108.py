# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0051_booking_end_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='check_out_time',
            new_name='checkout_time',
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='pick_up_time',
            new_name='pickup_time',
        ),
        migrations.AddField(
            model_name='booking',
            name='incomplete_reason',
            field=models.IntegerField(null=True, choices=[(1, 'Too Slow - somebody else booked your car'), (2, 'Owner Rejected - driver wasn\t approved'), (3, 'Driver Rejected - driver changed their mind'), (4, 'Missed - car rented out before we found a driver'), (5, 'Test - a booking that one of us created as a test'), (6, 'Canceled - driver canceled the booking thru the app')]),
        ),
        migrations.AddField(
            model_name='booking',
            name='incomplete_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='refund_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='requested_time',
            field=models.DateTimeField(null=True),
        ),
    ]
