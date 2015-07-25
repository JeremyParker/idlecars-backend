# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0043_fhvprovider'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FhvProvider',
            new_name='RideshareProvider',
        ),
    ]
