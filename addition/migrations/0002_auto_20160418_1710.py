# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0098_auto_20160418_1258'),
        ('addition', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='addition',
            name='first_name',
            field=models.CharField(max_length=30, verbose_name='first name', blank=True),
        ),
        migrations.AddField(
            model_name='addition',
            name='last_name',
            field=models.CharField(max_length=30, verbose_name='last name', blank=True),
        ),
        migrations.AddField(
            model_name='addition',
            name='owner',
            field=models.ForeignKey(related_name='additions', blank=True, to='server.Owner', null=True),
        ),
        migrations.AddField(
            model_name='addition',
            name='plate',
            field=models.CharField(max_length=24, blank=True),
        ),
    ]
