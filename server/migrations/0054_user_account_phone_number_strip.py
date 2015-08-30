# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from idlecars.fields import parse_phone_number
from server.models import UserAccount

def parse_user_account_phone(apps, schema_editor):
    for user_account in UserAccount.objects.all():
        user_account.phone_number = parse_phone_number(user_account.phone_number)
        user_account.save()
        print('.')


class Migration(migrations.Migration):
    dependencies = [
        ('server', '0053_auto_20150829_1151'),
    ]

    operations = [
        migrations.RunPython(parse_user_account_phone),
    ]
