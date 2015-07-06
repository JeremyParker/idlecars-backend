# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0036_20150701_flakes_too_slow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='email',
            field=models.CharField(blank=True, max_length=128, null=True, validators=[django.core.validators.EmailValidator()]),
        ),
    ]
