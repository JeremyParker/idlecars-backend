# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from idlecars.email import SendgridEmail

def send_welcome_email(to_address):
    return SendgridEmail().send_to(to_address)
