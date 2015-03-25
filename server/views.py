# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse

from idlecars.job_queue import job_queue

from server import jobs

def index(request):
    return JsonResponse({'cars': 'idle'})

def email(request):
    def email_address():
        return request.GET.get('address')

    if email_address():
        job_queue.enqueue(jobs.send_welcome_email, email_address())

        text = 'Im trying to send an email to {}'.format(email_address())
        return render(request, 'email.jade', { 'email_address': email_address() })
    else:
        return render(request, 'no_email.jade')
