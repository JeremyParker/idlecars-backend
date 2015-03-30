# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse

def index(request):
    return JsonResponse({'cars': 'idle'})
