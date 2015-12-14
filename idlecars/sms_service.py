# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from twilio.rest import TwilioRestClient
from django.conf import settings

from idlecars.job_queue import job_queue


'''
FakeSmsClient for testing.
'''
class FakeSmsClient(object):
    def __init__(self, ignored_sid, ignored_token):
        self.outbox = []

    class FakeResult(object):
        pass

    @property
    def messages(self):
        return self  # hack to avoid making a second fake class

    def create(self, from_=None, **kwargs):
        self.outbox.append(dict(kwargs))
        result = self.FakeResult()
        result.error_message = None
        return result

    def reset(self):
        self.outbox = []


def test_reset():
    if 'FakeSmsClient' == settings.SMS_IMPLEMENTATION:
        _client.reset()

def test_get_outbox():
    if 'FakeSmsClient' == settings.SMS_IMPLEMENTATION:
        return _client.outbox


'''
Real sms service stuff
'''
_client = vars()[settings.SMS_IMPLEMENTATION](
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN,
)


def send_sync(**kwargs):
    return _client.messages.create(from_=settings.TWILIO_PHONE_NUMBER, **kwargs)


def send_async(**kwargs):
    '''
    Parameters:
    to - the phone number to send to
    body - the body of the text messages
    media_urls - (optional) a list of urls for media to attach to the MMS
    '''
    return job_queue.enqueue(send_sync, **kwargs)
