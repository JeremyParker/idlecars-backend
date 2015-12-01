# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings


def password_reset(password_reset):
    parts = (settings.OWNER_APP_URL, '#', 'reset_password', password_reset.token)
    return '/'.join(parts)
