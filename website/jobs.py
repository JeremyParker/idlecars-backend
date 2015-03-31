# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from idlecars import email
from idlecars.job_queue import job_queue

from django.template import Context
from django.template.loader import get_template


def queue_driver_welcome_email(email_address):
    # render the template to HTML
    html = get_template('driver_welcome_email.html').render(Context({}))
    text = '''
    Welcome!
    Idlecars let’s you earn more money from rideshare by renting premium cars.
    
    Ask and you shall recieve
    Tell us what kind of car, and when you want to drive. We will find the right fit.

    support@idlecars.com
    '''

    job_queue.enqueue(
        _send_welcome_email,
        email_address,
        html,
        text,
    )


def queue_owner_welcome_email(email_address):
    # render the template to HTML
    html = get_template('owner_welcome_email.html').render(Context({}))
    text = '''
    Welcome!
    Find more drivers for your idle cars.

    List your car
    We’ll walk you through the process step-by-step. Just let us know when you want to rent it, and let us take care of the rest.

    support@idlecars.com
    '''

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
