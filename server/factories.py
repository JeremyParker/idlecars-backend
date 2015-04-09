# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
import random

from django.template.defaultfilters import slugify
from django.utils import timezone

from factory import LazyAttribute, lazy_attribute, BUILD_STRATEGY
from factory import DjangoModelFactory
import faker

from server import models

'''
Inspired by http://adamj.eu/tech/2014/09/03/factory-boy-fun/
'''

faker = faker.Factory.create()

class Factory(DjangoModelFactory):
    class Meta:
        abstract = True
        strategy = BUILD_STRATEGY


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
    date_joined = LazyAttribute(lambda o: timezone.now() - datetime.timedelta(days=random.randint(5, 50)))
    last_login = LazyAttribute(lambda o: o.date_joined + datetime.timedelta(days=4, hours=random.randint(0, 23)))


class User(Factory):
    class Meta:
        model = 'server.User'

    first_name = LazyAttribute(lambda o: faker.first_name())
    last_name = LazyAttribute(lambda o: faker.last_name())
    phone_number = LazyAttribute(lambda o: faker.phone_number())
    email = LazyAttribute(lambda o: o.first_name[0] + o.last_name + "@domain.com")


class Owner(Factory):
    class Meta:
        model = 'server.Owner'

    company_name = LazyAttribute(lambda o: faker.name() + "'s Cars")


class Car(Factory):
    class Meta:
        model = 'server.Car'
