# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0098_auto_20160418_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='plate',
            field=models.CharField(max_length=24, verbose_name='Medallion', blank=True),
        ),
    ]
