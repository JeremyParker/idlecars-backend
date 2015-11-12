# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('owner_crm', '0007_campaign'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='preferred_medium',
            field=models.IntegerField(default=1, choices=[(0, 'SMS'), (1, 'Email'), (2, 'SMS & Email')]),
        ),
    ]
