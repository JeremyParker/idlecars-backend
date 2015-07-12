# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0040_20150713_img_backfill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='make_model',
            field=models.ForeignKey(default=1, verbose_name='Make & Model', to='server.MakeModel'),
        ),
    ]
