# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import SubFactory

import idlecars.factory_helpers
from idlecars.factories import AuthUser

class PasswordReset(idlecars.factory_helpers.Factory):
    class Meta:
        model = 'owner_crm.PasswordReset'

    auth_user = SubFactory(AuthUser)
