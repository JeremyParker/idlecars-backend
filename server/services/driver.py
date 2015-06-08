# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.models import Driver

def create():
    return Driver.objects.create()
