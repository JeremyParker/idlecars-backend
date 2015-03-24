# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import sendgrid

class SendgridEmail:
    def __init__(self):
        # TODO: move this to env variable, duh
        self.sg = sendgrid.SendGridClient('app34610252@heroku.com', 'li2zhict')

    def send_to(self, address):
        message = sendgrid.Mail()
        message.add_to(address)
        message.set_subject('Welcome to idlecars')
        message.set_html('<h1>This is a test</h1>')
        message.set_text('This is a test')
        message.set_from('idlecars <info@idlecars.com>')
        return self.sg.send(message)
