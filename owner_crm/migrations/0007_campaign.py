# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('owner_crm', '0006_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=255)),
                ('preferred_method', models.IntegerField(default=0, choices=[(0, 'SMS'), (1, 'Email')])),
                ('notes', models.TextField(blank=True)),
            ],
        ),
    ]
