# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0054_user_account_phone_number_strip'),
    ]

    operations = [
        migrations.AddField(
            model_name='owner',
            name='merchant_account_state',
            field=models.IntegerField(null=True, choices=[(1, 'Pending'), (2, 'Approved'), (3, 'Declined')]),
        ),
    ]
