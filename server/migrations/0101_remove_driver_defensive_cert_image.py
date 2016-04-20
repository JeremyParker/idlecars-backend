# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0100_driver_ssn'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='driver',
            name='defensive_cert_image',
        ),
    ]
