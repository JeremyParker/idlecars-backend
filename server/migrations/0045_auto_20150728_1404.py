# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0044_auto_20150724_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='makemodel',
            name='body_type',
            field=models.IntegerField(blank=True, null=True, choices=[(0, 'Sedan'), (1, 'SUV')]),
        ),
        migrations.AddField(
            model_name='makemodel',
            name='lux_level',
            field=models.IntegerField(blank=True, null=True, choices=[(0, 'Standard'), (1, 'Luxury')]),
        ),
    ]
