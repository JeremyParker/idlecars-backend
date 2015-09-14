# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alternative',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.SlugField(help_text='Identifier can be made up from letters, digits, dashes and underscores.', max_length=16)),
                ('participant_count', models.IntegerField(default=0)),
                ('conversion_count', models.IntegerField(default=0)),
                ('ratio', models.FloatField(default=1, help_text='Whole number ratio of participants that will be assigned into this alternative')),
                ('created_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.SlugField(help_text='Identifier can be made up from letters, digits, dashes and underscores.', unique=True, max_length=64)),
                ('description', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('version', models.IntegerField(default=1)),
                ('created_time', models.DateTimeField(auto_now=True)),
                ('default', models.ForeignKey(related_name='+', default=None, blank=True, to='experiments.Alternative', null=True)),
                ('winner', models.ForeignKey(related_name='+', default=None, blank=True, to='experiments.Alternative', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='alternative',
            name='experiment',
            field=models.ForeignKey(to='experiments.Experiment'),
        ),
    ]
