# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def index(request):
    context = {
        'emails': [
            'foo@bar.com',
            'mcfly@delorean.net'
        ]
    }
    return render(request, 'index.jade', context)
