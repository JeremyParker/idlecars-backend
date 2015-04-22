# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0008_auto_20150412_1225'),
    ]

    operations = [
        migrations.CreateModel(
            name='MakeModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('make', models.CharField(max_length=128, blank=True)),
                ('model', models.CharField(max_length=128, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='car',
            name='make',
        ),
        migrations.RemoveField(
            model_name='car',
            name='model',
        ),
        migrations.AddField(
            model_name='car',
            name='make_model',
            field=models.ForeignKey(related_name='+', verbose_name='Make & Model', blank=True, to='server.MakeModel', null=True),
        ),
    ]
