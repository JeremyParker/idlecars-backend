# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0030_auto_20150609_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='address_proof_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='defensive_cert_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='driver_license_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='fhv_license_image',
            field=idlecars.model_helpers.StrippedCharField(max_length=100, blank=True),
        ),
    ]
