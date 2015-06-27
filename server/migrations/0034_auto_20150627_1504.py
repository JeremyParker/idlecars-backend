# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0033_auto_20150622_1342'),
    ]

    operations = [
        migrations.CreateModel(
            name='Insurance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('insurer_name', models.CharField(max_length=256, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='car',
            name='exterior_color',
            field=models.IntegerField(blank=True, null=True, choices=[(0, 'Black'), (1, 'Charcoal'), (2, 'Grey'), (3, 'Dark Blue'), (4, 'Blue'), (5, 'Tan')]),
        ),
        migrations.AddField(
            model_name='car',
            name='interior_color',
            field=models.IntegerField(blank=True, null=True, choices=[(0, 'Black'), (1, 'Charcoal'), (2, 'Grey'), (3, 'Dark Blue'), (4, 'Blue'), (5, 'Tan')]),
        ),
        migrations.AddField(
            model_name='car',
            name='last_known_mileage',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='last_mileage_update',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='insurance',
            field=models.ForeignKey(blank=True, to='server.Insurance', null=True),
        ),
    ]
