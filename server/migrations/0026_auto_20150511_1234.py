# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0025_auto_20150508_1352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='last_status_update',
            field=models.DateTimeField(),
        ),
    ]
