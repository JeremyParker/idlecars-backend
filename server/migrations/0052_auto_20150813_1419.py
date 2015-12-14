# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0051_booking_end_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='check_out_time',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='pick_up_time',
        ),
        migrations.AddField(
            model_name='booking',
            name='checkout_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='incomplete_reason',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'Too Slow - another driver on our system booked the car'), (2, 'Owner Rejected - driver wasn\t approved'), (3, 'Driver Rejected - driver changed their mind'), (4, 'Missed - car rented out elsewhere before we found a driver'), (5, 'Test - a booking that one of us created as a test'), (6, 'Canceled - driver canceled the booking thru the app')]),
        ),
        migrations.AddField(
            model_name='booking',
            name='incomplete_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='pickup_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='refund_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='requested_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='approval_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='return_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
