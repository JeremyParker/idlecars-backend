# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0038_driver_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='makemodel',
            name='image_filenames',
            field=models.TextField(help_text='Comma separated list of car image filenames. Each name must exist on our Amazon S3 bucket', blank=True),
        ),
    ]
