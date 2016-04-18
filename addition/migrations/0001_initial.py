# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Addition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=40, blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('driver_license_image', idlecars.model_helpers.StrippedCharField(max_length=300, blank=True)),
                ('fhv_license_image', idlecars.model_helpers.StrippedCharField(max_length=300, verbose_name='Hack License', blank=True)),
                ('defensive_cert_image', idlecars.model_helpers.StrippedCharField(max_length=300, verbose_name='Social Security Card', blank=True)),
                ('address_proof_image', idlecars.model_helpers.StrippedCharField(max_length=300, verbose_name='Motor Vehicle Record (MVR)', blank=True)),
                ('notes', models.TextField(blank=True)),
            ],
        ),
    ]
