# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_usermessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermessage',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
