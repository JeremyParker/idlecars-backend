# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0047_auto_20150724_2155'),
    ]

    operations = [
        migrations.CreateModel(
            name='RideshareFlavor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('friendly_id', models.CharField(unique=True, max_length=32)),
                ('compatible_models', models.ManyToManyField(to='server.MakeModel')),
            ],
        ),
        migrations.RemoveField(
            model_name='rideshareprovider',
            name='compatible_models',
        ),
        migrations.DeleteModel(
            name='RideshareProvider',
        ),
    ]
