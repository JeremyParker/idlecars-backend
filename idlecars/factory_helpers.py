# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import BUILD_STRATEGY
from factory import DjangoModelFactory
import faker


'''
Inspired by http://adamj.eu/tech/2014/09/03/factory-boy-fun/
'''

faker = faker.Factory.create()

class Factory(DjangoModelFactory):
    class Meta:
        abstract = True
        strategy = BUILD_STRATEGY
