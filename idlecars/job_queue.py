# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rq import Queue
from worker import conn

job_queue = Queue(connection=conn)
