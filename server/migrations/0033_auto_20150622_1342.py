# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0032_auto_20150610_1201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='address_proof_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=300, blank=True),
        ),
        migrations.AlterField(
            model_name='driver',
            name='defensive_cert_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=300, blank=True),
        ),
        migrations.AlterField(
            model_name='driver',
            name='driver_license_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=300, blank=True),
        ),
        migrations.AlterField(
            model_name='driver',
            name='fhv_license_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=300, blank=True),
        ),
    ]
