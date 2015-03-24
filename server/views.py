# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import JsonResponse
from django.http import HttpResponse

def index(request):
    return JsonResponse({'cars': 'idle'})

def email(request):
    # import pdb; pdb.set_trace()
    if request.GET.has_key('address'):
        text = 'Im trying to send an email to {address}'.format(**request.GET)
        return HttpResponse(text)
    else:
        return HttpResponse("<h1>Add an address param please!</h1>")
