# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import JsonResponse
from django.http import HttpResponse

from server import jobs
from idlecars.job_queue import job_queue

def index(request):
    return JsonResponse({'cars': 'idle'})

def email(request):
    def email_address():
        return request.GET.get('address')

    if email_address():
        job_queue.enqueue(jobs.send_welcome_email, email_address())

        text = 'Im trying to send an email to {}'.format(email_address())
        return HttpResponse('<h1>{text}</h1>'.format(**locals()))
    else:
        return HttpResponse("<h1>Add an address param please!</h1>")
