# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_type', models.IntegerField(default=0, choices=[(0, 'Integer'), (0, 'Float'), (0, 'String'), (0, 'JSON'), (0, 'Boolean')])),
                ('key', models.CharField(unique=True, max_length=255)),
                ('value', models.TextField(blank=True)),
                ('units', models.CharField(max_length=255, blank=True)),
                ('comment', models.TextField(blank=True)),
            ],
        ),
    ]
