# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0028_driver'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='driver',
            field=models.ForeignKey(to='server.Driver', null=True),
        ),
        migrations.AlterField(
            model_name='driver',
            name='documentation_complete',
            field=models.BooleanField(default=False, verbose_name='docs confirmed'),
        ),
    ]
