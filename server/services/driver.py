# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.models import Driver

def create():
    return Driver.objects.create()


def update(driver):
    # if documents are now complete and not approved, send an email to ops


    driver.auth_user.save()
    driver.save()
