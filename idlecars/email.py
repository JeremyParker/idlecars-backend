# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import os

import sendgrid

class SendgridEmail(object):
    def __init__(self):
        # get these values from 'heroku config' tool
        username = os.getenv('SENDGRID_USERNAME')
        password = os.getenv('SENDGRID_PASSWORD')

        if not (username and password):
            return

        self.client = sendgrid.SendGridClient(username, password)

    def send_to(self, address):
        if not hasattr(self, 'client'):
            return

        message = sendgrid.Mail()
        message.add_to(address)
        message.set_subject('Welcome to idlecars')
        message.set_html('<h1>This is a test</h1>')
        message.set_text('This is a test')
        message.set_from('idlecars <info@idlecars.com>')
        return self.client.send(message)
