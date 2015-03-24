# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import JsonResponse
from django.http import HttpResponse

def index(request):
    return JsonResponse({'cars': 'idle'})

def email(request):
    return HttpResponse("<h1>I'm trying to send an email</h1>")
