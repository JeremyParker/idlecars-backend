# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0102_driver_no_mvr'),
    ]

    operations = [
        migrations.CreateModel(
            name='Removal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('hack_license_number', models.CharField(max_length=7, verbose_name='hack_license_number', blank=True)),
                ('notes', models.TextField(blank=True)),
                ('owner', models.ForeignKey(related_name='removals', blank=True, to='server.Owner', null=True)),
            ],
        ),
    ]
