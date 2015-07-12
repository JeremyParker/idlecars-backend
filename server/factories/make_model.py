# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import LazyAttribute

from idlecars.factory_helpers import Factory, faker
from server import models


class MakeModel(Factory):
    class Meta:
        model = 'server.MakeModel'
    make = LazyAttribute(lambda o: faker.last_name())
    model = LazyAttribute(lambda o: faker.last_name())

class MakeModelWithImage(MakeModel):
    image_filenames = 'tacocat.jpg'

class MakeModelWithImages(MakeModel):
    image_filenames = 'tacocat.jpg, oprah_amazing.gif'
