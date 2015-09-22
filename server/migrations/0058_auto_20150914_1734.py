# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0057_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('status', models.IntegerField(default=0, choices=[(0, 'Pending gateway response'), (1, 'Payment approved'), (2, 'Payment declined'), (3, 'Card rejected')])),
                ('error_message', models.CharField(max_length=256)),
                ('transaction_id', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gateway_name', models.CharField(max_length=16)),
                ('gateway_token', models.CharField(max_length=256)),
                ('suffix', models.CharField(max_length=4)),
                ('card_type', models.CharField(max_length=32)),
                ('card_logo', models.CharField(max_length=256)),
                ('expiration_date', models.DateField(default=None, null=True, blank=True)),
                ('unique_number_identifier', models.CharField(max_length=32)),
                ('driver', models.ForeignKey(to='server.Driver')),
            ],
        ),
        migrations.AlterField(
            model_name='booking',
            name='deprecated_state',
            field=models.IntegerField(default=0, choices=[(0, 'State comes from event times, not from this field.'), (1, 'Pending - waiting for driver docs'), (2, 'Complete - driver uploaded all docs'), (3, 'Requested - waiting for owner/insurance'), (4, 'Accepted - waiting for deposit, ssn, contract'), (5, 'Booked - car marked busy with new available_time'), (6, "Flake - Didn't Submit Docs in 24 hours"), (7, 'Too Slow - somebody else booked your car'), (8, 'Owner Rejected - driver wasn\t approved'), (9, 'Driver Rejected - driver changed their mind'), (10, 'Missed - car rented out before we found a driver'), (11, 'Test - a booking that one of us created as a test'), (12, 'Canceled - driver canceled the booking thru the app')]),
        ),
        migrations.AddField(
            model_name='payment',
            name='booking',
            field=models.ForeignKey(to='server.Booking'),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.ForeignKey(blank=True, to='server.PaymentMethod', null=True),
        ),
    ]
