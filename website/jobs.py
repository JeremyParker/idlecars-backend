# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.template import Context
from django.template.loader import get_template
from django.utils.http import urlquote

from idlecars import email
from idlecars.job_queue import job_queue

def queue_driver_welcome_email(email_address):
    def _reply_email_subject():
        return urlquote("I want to drive!")

    def _reply_email_body():
        text = '''
        What kind of car are you looking for?

        When do you need it?
        '''
        return urlquote(text)

    def _cta_href():
        return 'mailto:support@idlecars.com?subject={subject}&body={body}'.format(
            subject=_reply_email_subject(),
            body=_reply_email_body(),
        )

    context = Context({
        'message': 'Earn more money from rideshare by renting premium cars.',
        'instruction_header': 'Ask and you shall recieve',
        'instructions': 'Tell us what kind of car, and when you want to drive. We will find the right fit.',
        'cta': 'Request a car',
        'cta_href': _cta_href(),
    })
    html = get_template('welcome_email.html').render(context)

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
    context = Context({
        'message': 'Find more drivers for your idle cars.',
        'instruction_header': 'List your car',
        'instructions': 'Fill out this form to add your car our listings. When a qualified driver requests your car, we will contact you directly.',
        'cta': 'List a car',
        'cta_href': 'http://goo.gl/forms/4s26I6GUQY',
    })
    html = get_template('welcome_email.html').render(context)

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
