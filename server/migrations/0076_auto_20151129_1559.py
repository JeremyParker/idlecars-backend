# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0075_auto_20151123_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='insurance_policy_number',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='insurance',
            name='insurance_code',
            field=models.CharField(max_length=8, unique=True, null=True, blank=True),
        ),
    ]
