# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rq import Queue
from worker import conn

from django.conf import settings


class RealQueue(Queue):
    pass


class FakeQueue(object):
    def __init__(self, connection):
        pass

    def enqueue(self, func, *args, **kwargs):
        print args[0].__dict__
        return func(*args, **kwargs)

job_queue = vars()[settings.QUEUE_IMPLEMENTATION](connection=conn)
