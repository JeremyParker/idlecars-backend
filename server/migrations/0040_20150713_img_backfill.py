# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def backfill_make_model_images(apps, schema_editor):
    MakeModel = apps.get_model("server", "MakeModel")

    for mm in MakeModel.objects.all():
        mm.image_filenames = mm.image_filename
        mm.save()
        print('.')


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0039_makemodel_image_filenames'),
    ]

    operations = [
        migrations.RunPython(backfill_make_model_images),
    ]
