# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import mandrill
import json

from django.conf import settings
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


class Unsubscribes(object):
    def __init__(self):
        self.client = mandrill.Mandrill(settings.MANDRILL_API_KEY)

    def all(self):
        return self.client.rejects.list(include_expired=False)


@staff_member_required
def index(request):
    def _templatify(unsubscribe):
        return (
            unsubscribe.get('created_at'),
            unsubscribe.get('email'),
            unsubscribe.get('reason'),
            )

    unsubscribes = (_templatify(unsub) for unsub in Unsubscribes().all())
    return render(request, 'index.html', {'unsubscribes': unsubscribes})
