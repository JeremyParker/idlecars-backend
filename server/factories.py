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

def lazy(func):
    return LazyAttribute(lambda o: func())

class Factory(DjangoModelFactory):
    class Meta:
        abstract = True
        strategy = BUILD_STRATEGY


class StaffUser(Factory):
    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username',)

    first_name = lazy(faker.first_name)
    last_name = lazy(faker.last_name)
    username = LazyAttribute(lambda o: slugify('{0} {1}'.format(o.first_name, o.last_name)))
    email = LazyAttribute(lambda o: o.username + "@idlecars.com")
    is_staff = True
    is_superuser = True
    date_joined = lazy(lambda: timezone.now() - datetime.timedelta(days=random.randint(5, 50)))
    last_login = LazyAttribute(lambda o: o.date_joined + datetime.timedelta(days=4, hours=random.randint(0, 23)))


class FleetPartner(Factory):
    class Meta:
        model = 'server.FleetPartner'

    name = faker.name() + "'s " + random.choice(["cabs", "car service", "fleet", "limosine service"])
    contact = faker.first_name() + ' ' + faker.last_name()
    phone_number = lazy(faker.phone_number)
    @lazy_attribute
    def email(self):
        domain = 'example.' + random.choice(['com', 'org'])
        return '{}.@{}'.format(
            self.contact,
            domain,
        )


class Driver(Factory):
    class Meta:
        model = 'server.Driver'

    first_name = lazy(faker.first_name)
    last_name = lazy(faker.last_name)

    @lazy_attribute
    def email(self):
        domain = 'example.' + random.choice(['com', 'org'])
        return '{}.{}.{}@{}'.format(
            self.first_name,
            self.last_name,
            random.choice(['loves.kittens', 'princess', '1337']),
            domain,
        )

    phone_number = lazy(faker.phone_number)

    @lazy_attribute
    def email_verified(self):
        return timezone.now() - datetime.timedelta(days=random.randint(2, 10))
