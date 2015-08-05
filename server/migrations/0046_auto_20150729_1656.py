# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0045_auto_20150728_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='makemodel',
            name='body_type',
            field=models.IntegerField(default=0, choices=[(0, 'Sedan'), (1, 'SUV')]),
        ),
        migrations.AlterField(
            model_name='makemodel',
            name='lux_level',
            field=models.IntegerField(default=0, choices=[(0, 'Standard'), (1, 'Luxury')]),
        ),
    ]
