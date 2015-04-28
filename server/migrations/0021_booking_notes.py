# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0020_booking_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='notes',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
