# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0013_auto_20150415_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='min_lease',
            field=idlecars.model_helpers.ChoiceField(default='No Minimum', max_length=32, choices=[(b'_00_unknown', 'Unknown'), (b'_01_no_min', 'No'), (b'_02_one_week', 'One Week'), (b'_03_two_weeks', 'Two Weeks'), (b'_04_three_weeks', 'Three Weeks'), (b'_05_one_month', 'One Month'), (b'_06_six_weeks', 'Six Weeks'), (b'_07_two_months', 'Two Months'), (b'_08_three_months', 'Three Months'), (b'_09_four_months', 'Four Months'), (b'_10_five_months', 'Five Months'), (b'_11_six_months', 'Six Months')]),
            preserve_default=True,
        ),
    ]
