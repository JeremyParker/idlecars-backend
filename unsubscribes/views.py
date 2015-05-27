# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import mandrill
import json

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
            '/admin/unsubscribes',
            )

    def _index(request):
        unsubscribes = (_templatify(unsub) for unsub in Unsubscribes().all())
        return render(request, 'index.jade', {'unsubscribes': unsubscribes})

    def _delete(request):
        email = request.POST.get('email')
        print request.POST
        if email:
            Unsubscribes().ununsubscribe(email)
        return redirect('/admin/unsubscribes')

    if request.method == 'POST':
        return _delete(request)
    else:
        return _index(request)
