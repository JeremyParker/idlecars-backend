# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0012_auto_20150414_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='min_lease',
            field=idlecars.model_helpers.ChoiceField(default='No Minimum', max_length=32, choices=[(b'_0_unknown', 'Unknown'), (b'_1_no_min', 'No'), (b'_2_one_week', 'One Week'), (b'_3_two_weeks', 'Two Weeks'), (b'_4_three_weeks', 'Three Weeks'), (b'_5_one_month', 'One Month'), (b'_6_six_weeks', 'Six Weeks'), (b'_7_two_months', 'Two Months')]),
            preserve_default=True,
        ),
    ]
