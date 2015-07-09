# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0037_auto_20150706_1007'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
