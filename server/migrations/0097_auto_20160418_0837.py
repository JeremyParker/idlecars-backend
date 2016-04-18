# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0096_auto_20160417_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='min_lease',
            field=idlecars.model_helpers.ChoiceField(default='_01_no_min', max_length=32, choices=[(b'_00_unknown', 'Unknown'), (b'_01_no_min', 'No'), (b'_02_one_week', '7 days'), (b'_03_two_weeks', '14 days'), (b'_04_three_weeks', '21 days'), (b'_05_one_month', '30 days'), (b'_06_six_weeks', '45 days'), (b'_07_two_months', '60 days'), (b'_08_three_months', '90 days'), (b'_09_four_months', '120 days'), (b'_10_five_months', '150 days'), (b'_11_six_months', '180 days')]),
        ),
    ]
