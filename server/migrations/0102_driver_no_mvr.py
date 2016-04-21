# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0101_remove_driver_defensive_cert_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='no_mvr',
            field=models.BooleanField(default=False, verbose_name="Driver doesn't have an MVR"),
        ),
    ]
