# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

import forms


'''
View that presents the landing page and a simple 'subscribe' form.
'''
def index(request):
    form = forms.DriverProspectForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            return HttpResponseRedirect('/survey/')

    return render(request, 'landing_page.html', {'form': form})


'''
View to handle the submission of survey page form, store form info and respond with
a thank you message.
'''
def survey(request):
    return HttpResponse("Thanks.")
