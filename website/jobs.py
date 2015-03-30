# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404

from idlecars import email
from idlecars.job_queue import job_queue

import models


def queue_driver_welcome_email(email_address):
    job_queue.enqueue(_send_driver_welcome_email, email_address)


def queue_owner_welcome_email(email_address):
    job_queue.enqueue(_send_owner_welcome_email, email_address)


def _send_driver_welcome_email(email_address):
    html = '<h1>This is a test of the driver email</h1>'
    text = 'This is a test of the driver email'
    return email.SendgridEmail().send_to(
        address = email_address,
        subject = 'Welcome to idlecars',
        html = html,
        text = text,
    )


def _send_owner_welcome_email(email_address):
    html = '<h1>This is a test of the owner email</h1>'
    text = 'This is a test of the owner email'
    return email.SendgridEmail().send_to(
        address = email_address,
        subject = 'Welcome to idlecars',
        html = html,
        text = text,
    )
