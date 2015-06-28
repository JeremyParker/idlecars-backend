# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renewal',
            name='car',
            field=models.ForeignKey(related_name='renewals', to='server.Car'),
        ),
        migrations.AlterField(
            model_name='renewal',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='renewal',
            name='updated_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
