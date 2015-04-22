# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
import random

from django.template.defaultfilters import slugify
from django.utils import timezone

from factory import LazyAttribute

from idlecars.factory_helpers import Factory, faker


class StaffUser(Factory):
    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username',)

    first_name = LazyAttribute(lambda o: faker.first_name())
    last_name = LazyAttribute(lambda o:faker.last_name())
    username = LazyAttribute(lambda o: slugify('{0} {1}'.format(o.first_name, o.last_name)))
    email = LazyAttribute(lambda o: o.username + "@idlecars.com")
    is_staff = True
    is_superuser = True
    date_joined = LazyAttribute(
        lambda o: timezone.now() - datetime.timedelta(days=random.randint(5, 50))
    )
    last_login = LazyAttribute(
        lambda o: o.date_joined + datetime.timedelta(days=4, hours=random.randint(0, 23))
    )
