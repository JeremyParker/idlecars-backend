# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addition', '0004_addition_created_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='addition',
            name='defensive_cert_image',
        ),
        migrations.AddField(
            model_name='addition',
            name='ssn',
            field=models.CharField(max_length=9, blank=True),
        ),
    ]
