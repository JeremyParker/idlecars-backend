# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0049_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='makemodel',
            name='passenger_count',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
