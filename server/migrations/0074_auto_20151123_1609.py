# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0073_auto_20151106_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='exterior_color',
            field=models.IntegerField(blank=True, null=True, choices=[(0, 'Black'), (1, 'Charcoal'), (2, 'Grey'), (3, 'Dark Blue'), (4, 'Blue'), (5, 'Tan'), (6, 'White')]),
        ),
        migrations.AlterField(
            model_name='car',
            name='interior_color',
            field=models.IntegerField(blank=True, null=True, choices=[(0, 'Black'), (1, 'Charcoal'), (2, 'Grey'), (3, 'Dark Blue'), (4, 'Blue'), (5, 'Tan'), (6, 'White')]),
        ),
    ]
