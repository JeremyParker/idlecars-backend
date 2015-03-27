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
            raise RuntimeError("email username/password are not set in this environment.")

        self.client = sendgrid.SendGridClient(username, password)

    def send_to(self, address, subject, html, text, cc = None):
        if not hasattr(self, 'client'):
            raise RuntimeError("There is no email client available.")

        message = sendgrid.Mail()
        message.add_to(address)
        message.set_subject(subject)
        message.set_html(html)
        message.set_text(text)
        message.set_from('idlecars <info@idlecars.com>')
        return self.client.send(message)
