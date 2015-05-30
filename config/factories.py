# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random

from factory import LazyAttribute, SelfAttribute

from idlecars.factory_helpers import Factory, faker
from config import models

data_type_functions = {
    models.INTEGER_TYPE : lambda o: '45',
    models.FLOATING_TYPE : '2',
    models.STRING_TYPE : '2',
    models.JSON_TYPE : '2',
    models.BOOLEAN_TYPE : '2',
}

def _get_value(data_type):
    import pdb; pdb.set_trace()
    return data_type_functions[self.data_type]()

class Config(Factory):
    class Meta:
        model = 'config.Config'

    data_type = LazyAttribute(lambda o: random.choice([
        models.INTEGER_TYPE,
        models.FLOATING_TYPE,
        models.STRING_TYPE,
        models.JSON_TYPE,
        models.BOOLEAN_TYPE,
    ]))

    key = faker.word()
    value = LazyAttribute(_get_value(SelfAttribute('data_type')))
    units = 'widgets'
    comment = 'placeholder text where the comment would be'
