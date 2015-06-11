# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server import models
from django.contrib.auth import get_user_model

def get_phone(number):
    return ''.join(x for x in number if x.isdigit())


def run_backfill():
    User = get_user_model()

    for driver in models.Driver.objects.all():
        user_account = models.UserAccount.objects.get(driver=driver)
        if not user_account:
            print('what the hell? No user account for driver {}!'.format(unicode(driver)))
            continue

        if User.objects.filter(username=get_phone(user_account.phone_number)).exists():
            existing_auth_user = User.objects.get(username=get_phone(user_account.phone_number))
            existing_driver = models.Driver.objects.get(auth_user=existing_auth_user)

            # reassign bookings to the existing driver
            for b in models.Booking.objects.filter(driver=driver).all():
                b.driver = existing_driver
                b.save()

            print('driver with duplicate phone number found')
            print('{}'.format(user_account.first_name))
            print('{}'.format(user_account.last_name))
            print('{}'.format(user_account.phone_number))
            print('{}'.format(user_account.email))

            models.UserAccount.objects.get(driver=driver).delete()
            models.Driver.objects.get(pk=driver.pk).delete()
        else:
            new_user = User.objects.create_user(
                username=get_phone(user_account.phone_number),
                password='1dleC@rs',
                email=user_account.email,
                first_name=user_account.first_name,
                last_name=user_account.last_name,
            )
            # overwrite the auto-assigned 'now' that create_user assigns
            if user_account.created_time:
                new_user.date_joined = user_account.created_time
                new_user.save()

            driver.auth_user = new_user
            driver.save()
        models.UserAccount.objects.get(driver=driver).delete()
        print('.')
