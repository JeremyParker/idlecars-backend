# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from idlecars.email import SendgridEmail
from idlecars.job_queue import job_queue


def queue_welcome_email(to_address):
    job_queue.enqueue(_send_welcome_email, to_address)


def _send_welcome_email(to_address):
    return SendgridEmail().send_to(
        address = to_address,
        subject = 'Welcome to idlecars',
        html = '<h1>This is a test</h1>',
        text = 'This is a test',
    )
