# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import os

import sendgrid

from django.core.mail import EmailMessage

from idlecars.job_queue import job_queue


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
        message.set_from('idlecars <support@idlecars.com>')
        message.add_bcc('support@idlecars.com')
        return self.client.send(message)


def _send_now(msg):
    return msg.send()


def setup_email(template_name, subject, merge_vars):
    msg = EmailMessage(
        subject=subject,
        from_email="support@idlecars.com",
        to=merge_vars.keys()
    )
    msg.template_name = template_name
    msg.merge_vars = merge_vars
    return msg


def send_async(**kwargs):
    '''
    Send an email on a different thread.
    '''
    msg = setup_email(**kwargs)
    job_queue.enqueue(_send_now, msg)


def send_sync(**kwargs):
    '''
    Send an email on this thread.
    '''
    msg = setup_email(**kwargs)
    _send_now(msg)
    return msg
