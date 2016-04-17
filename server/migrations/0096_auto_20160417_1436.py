# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0095_auto_20160416_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='refund_time',
            field=models.DateTimeField(null=True, verbose_name='Removal time', blank=True),
        ),
        migrations.AlterField(
            model_name='car',
            name='shift',
            field=models.IntegerField(default=0, choices=[(0, 'Unknown'), (1, '24/7'), (2, 'Day Shift'), (3, 'Night Shift'), (4, '')]),
        ),
        migrations.AlterField(
            model_name='driver',
            name='address_proof_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=300, verbose_name='Motor Vehicle Record (MVR)', blank=True),
        ),
        migrations.AlterField(
            model_name='driver',
            name='defensive_cert_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=300, verbose_name='Social Security Card', blank=True),
        ),
        migrations.AlterField(
            model_name='driver',
            name='fhv_license_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=300, verbose_name='Hack License', blank=True),
        ),
    ]
