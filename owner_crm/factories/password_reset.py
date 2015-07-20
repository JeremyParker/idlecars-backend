# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import SubFactory

import idlecars.factory_helpers
from server import factories

class PasswordReset(idlecars.factory_helpers.Factory):
    class Meta:
        model = 'owner_crm.PasswordReset'

    auth_user = SubFactory(factories.AuthUser)
