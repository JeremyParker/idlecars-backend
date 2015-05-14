# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from config import models


def get_all_parsed_config():
    config = {}
    for c in models.Config.objects.all():
        config[config.key] = c.get_data()
    return config


class DefaultValue:
    pass

def get(key, default=DefaultValue):
    config = get_all_parsed_config()
    if key in config:
        return config[key]
    else:
        if default is not DefaultValue:
            return default
        else:
            raise KeyError(key)
