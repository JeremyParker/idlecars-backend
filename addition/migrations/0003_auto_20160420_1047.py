# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addition', '0002_auto_20160418_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='addition',
            name='mvr_authorized',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='addition',
            name='plate',
            field=models.CharField(max_length=24, verbose_name='Medallion', blank=True),
        ),
    ]
