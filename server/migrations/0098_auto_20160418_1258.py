# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0097_auto_20160418_0837'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='car',
            options={'verbose_name': 'Shift', 'verbose_name_plural': 'Shifts'},
        ),
        migrations.AddField(
            model_name='owner',
            name='social',
            field=models.CharField(blank=True, max_length=4, verbose_name='Last 4 of SSN', validators=[django.core.validators.RegexValidator('^[0-9]+$', 'Only numbers are allowed in a zip code.', 'Invalid zip'), django.core.validators.MinLengthValidator(4), django.core.validators.MaxLengthValidator(4)]),
        ),
        migrations.AlterField(
            model_name='makemodel',
            name='image_filenames',
            field=models.TextField(help_text='Comma separated list of car image filenames. Each name must exist on our Google driver folder', blank=True),
        ),
    ]
