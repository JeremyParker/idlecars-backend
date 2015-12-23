# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identity', models.CharField(max_length=256)),
                ('converted_time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='alternative',
            name='conversion_count',
        ),
        migrations.RemoveField(
            model_name='alternative',
            name='participant_count',
        ),
        migrations.AddField(
            model_name='assignment',
            name='alternative',
            field=models.ForeignKey(blank=True, to='experiments.Alternative', null=True),
        ),
        migrations.AddField(
            model_name='assignment',
            name='experiment',
            field=models.ForeignKey(to='experiments.Experiment'),
        ),
    ]
