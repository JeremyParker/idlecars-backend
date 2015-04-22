# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0011_auto_20150414_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='make_model',
            field=models.ForeignKey(related_name='+', verbose_name='Make & Model', blank=True, to='server.MakeModel', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='email',
            field=models.CharField(blank=True, max_length=128, unique=True, null=True, validators=[django.core.validators.EmailValidator()]),
            preserve_default=True,
        ),
    ]
