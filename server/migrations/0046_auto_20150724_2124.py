# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0045_rideshareprovider_frieldly_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rideshareprovider',
            name='frieldly_id',
            field=models.CharField(unique=True, max_length=32),
        ),
    ]
