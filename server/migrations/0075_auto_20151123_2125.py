# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0074_auto_20151123_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='active_in_tlc',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='car',
            name='base_address',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='base_number',
            field=models.CharField(max_length=16, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='base_telephone_number',
            field=models.CharField(max_length=16, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='base_type',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'Livery'), (2, 'Paratrans')]),
        ),
        migrations.AddField(
            model_name='car',
            name='expiration_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='found_in_tlc',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='car',
            name='last_updated',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='registrant_name',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='vehicle_vin_number',
            field=models.CharField(max_length=32, blank=True),
        ),
    ]
