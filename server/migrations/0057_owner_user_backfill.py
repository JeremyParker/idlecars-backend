# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth import get_user_model

from server.services import auth_user as auth_user_service


def backfill_copy_user_account_to_user(apps, schema_editor):
    Owner = apps.get_model("server", "Owner")
    User = get_user_model()
    for owner in Owner.objects.all():
        for user_account in owner.user_account_set.all():
            try:
                auth_user = User.objects.get(username=phone_number)
            except User.DoesNotExist:
                auth_user = auth_user_service.create_auth_user(user_account)
                print 'created new auth user {} {}, {}, {}'.format(
                    auth_user.first_name,
                    auth_user.last_name,
                    auth_user.username,
                    auth_user.email,
                )

            if not auth_user in owner.auth_users.all():
                owner.auth_users.add(auth_user)
                print 'added auth user {} to {}'.format(
                    auth_user.pk,
                    owner.name(),
                )
        print('.\n')


def backfill_copy_user_to_auth_account(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('server', '0056_driver_braintree_customer_id'),
    ]

    operations = [
        migrations.RunPython(
            backfill_copy_user_account_to_user,
            reverse_code=backfill_copy_user_to_auth_account
        ),
    ]
