# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0044_auto_20150724_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='rideshareprovider',
            name='frieldly_id',
            field=models.CharField(default='uber_x', max_length=32),
            preserve_default=False,
        ),
    ]
