# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from idlecars import email
from idlecars.job_queue import job_queue

from django.template import Context
from django.template.loader import get_template


def queue_driver_welcome_email(email_address):
    # render the template to HTML
    html = get_template('welcome_email.html').render(
        Context({
            'title': 'Title',
            'body': 'Body',
        })
    )
    text = ''  # TODO(JP)
    job_queue.enqueue(
        _send_welcome_email,
        email_address,
        html,
        text
    )


def queue_owner_welcome_email(email_address):
    # render the template to HTML
    html = get_template('welcome_email.html').render(
        Context({
            'title': 'Title',
            'body': 'Body',
        })
    )
    text = ''  # TODO(JP)
    job_queue.enqueue(
        _send_welcome_email,
        email_address,
        html,
        text,
    )


def _send_welcome_email(email_address, html, text):
    return email.SendgridEmail().send_to(
        address = email_address,
        subject = 'Welcome to idlecars',
        html = html,
        text = text,
    )
