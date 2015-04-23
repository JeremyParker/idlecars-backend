# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0016_auto_20150423_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='base',
            field=models.CharField(max_length=64, blank=True),
            preserve_default=True,
        ),
    ]
