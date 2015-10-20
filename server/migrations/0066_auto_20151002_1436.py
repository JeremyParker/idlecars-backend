# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0065_auto_20150921_2029'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='base_letter',
            field=idlecars.model_helpers.StrippedCharField(max_length=300, blank=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='base_letter_rejected',
            field=models.BooleanField(default=False, verbose_name='base letter rejected'),
        ),
        migrations.AlterField(
            model_name='owner',
            name='service_percentage',
            field=models.DecimalField(null=True, verbose_name='Negotiated service percentage', max_digits=10, decimal_places=4, blank=True),
        ),
    ]
