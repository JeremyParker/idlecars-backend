# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_auto_20150414_1545'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=40, blank=True)),
                ('email', models.CharField(max_length=40, verbose_name='Email Address', blank=True)),
                ('message', models.TextField(blank=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
