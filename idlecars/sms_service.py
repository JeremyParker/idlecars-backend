# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from twilio.rest import TwilioRestClient
from django.conf import settings

from idlecars.job_queue import job_queue


_client = None

def _get_client():
    global _client
    if not _client:
        _client = TwilioRestClient(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
        )
    return _client


def _send_now(kwargs):
    return _get_client().messages.create(from_=settings.TWILIO_PHONE_NUMBER, **kwargs)


def send_sync(**kwargs):
    return _send_now(kwargs)


def send_async(**kwargs):
    '''
    Parameters:
    to - the phone number to send to
    body - the body of the text messages
    media_urls - (optional) a list of urls for media to attach to the MMS
    '''
    job_queue.enqueue(_send_now, kwargs)
