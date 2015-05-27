# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import mandrill
import json

from django.core import urlresolvers
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required


class Unsubscribes(object):
    def __init__(self):
        self.client = mandrill.Mandrill(settings.MANDRILL_API_KEY)

    def all(self):
        return self.client.rejects.list(include_expired=False)

    def ununsubscribe(self, email):
        self.client.rejects.delete(email)


@staff_member_required
def index(request):
    def _templatify(unsubscribe):
        return (
            unsubscribe.get('created_at'),
            unsubscribe.get('email'),
            unsubscribe.get('reason'),
            urlresolvers.reverse('unsubscribes:ununsubscribe')
            )

    unsubscribes = (_templatify(unsub) for unsub in Unsubscribes().all())
    return render(request, 'index.jade', {'unsubscribes': unsubscribes})

@staff_member_required
def ununsubscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            Unsubscribes().ununsubscribe(email)

    return redirect('unsubscribes:index')
