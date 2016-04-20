# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0099_auto_20160420_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='ssn',
            field=models.CharField(max_length=9, blank=True),
        ),
    ]
