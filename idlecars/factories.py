# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import auth

from factory import LazyAttribute, post_generation
from factory.django import DjangoModelFactory

from idlecars.factory_helpers import faker, random_phone


class AuthUser(DjangoModelFactory):
    class Meta:
        model = auth.get_user_model()
        django_get_or_create = ('username',)

    first_name = LazyAttribute(lambda o: faker.first_name())
    last_name = LazyAttribute(lambda o:faker.last_name())
    username = LazyAttribute(lambda o: random_phone())
    email = LazyAttribute(lambda o: faker.free_email())

    @post_generation
    def password(self, create, value, **kwargs):
        self.set_password(value or 'password')
        if create:
            self.save()


class StaffUser(AuthUser):
    is_staff = True
    is_superuser = True
