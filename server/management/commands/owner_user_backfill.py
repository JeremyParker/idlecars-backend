# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from server.models import Owner
from server.services import auth_user as auth_user_service


class Command(BaseCommand):
    help = '''
    This command creates auth.User objects for every owner's server.models.UserAccount
    object, if necessary.
    '''

    def backfill_copy_user_account_to_user(self):
        for owner in Owner.objects.all():
            for user_account in owner.user_account.all():
                if not user_account.phone_number:
                    print 'no phone for account {}\n'.format(user_account.email)
                    continue
                try:
                    auth_user = User.objects.get(username=user_account.phone_number)
                    print 'reusing a user for user_account {} {}, {}, {}\n'.format(
                        user_account.first_name,
                        user_account.last_name,
                        user_account.phone_number,
                        user_account.email,
                    )
                except User.DoesNotExist:
                    auth_user = auth_user_service.create_auth_user(user_account)
                    print 'created new auth user {} {}, {}, {}\n'.format(
                        auth_user.first_name,
                        auth_user.last_name,
                        auth_user.username,
                        auth_user.email,
                    )

                if not auth_user in owner.auth_users.all():
                    owner.auth_users.add(auth_user)
                    print 'added auth user {} to {}\n'.format(
                        auth_user.pk,
                        owner.name(),
                    )
            print('.\n')


    def handle(self, *args, **options):
        self.backfill_copy_user_account_to_user()
