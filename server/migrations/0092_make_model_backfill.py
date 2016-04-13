# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def backfill_make_models(apps, schema_editor):
    MakeModel = apps.get_model("server", "MakeModel")

    make_models = [
        {'make': 'Toyota', 'model': 'Prius-v'},
        {'make': 'Toyota', 'model': 'Camry'},
        {'make': 'Toyota', 'model': 'Rav 4'},
        {'make': 'Toyota', 'model': 'Highlander'},
        {'make': 'Nissan', 'model': 'NV-200'},
        {'make': 'Nissan', 'model': 'NV-200 WAV'},
        {'make': 'Ford', 'model': 'C-Max'},
        {'make': 'Ford', 'model': 'Escape'},
    ]
    for mm in make_models:
        try:
            MakeModel.objects.create(**mm)
        except Error as e:
            print e
        print('.')


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0091_auto_20160107_0941'),
    ]

    operations = [
        migrations.RunPython(
            backfill_make_models,
            reverse_code=migrations.RunPython.noop
        ),
    ]
