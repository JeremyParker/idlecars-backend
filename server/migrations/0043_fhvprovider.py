# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0042_auto_20150724_1100'),
    ]

    operations = [
        migrations.CreateModel(
            name='FhvProvider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('compatible_models', models.ManyToManyField(to='server.MakeModel')),
            ],
        ),
    ]
