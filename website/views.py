# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

from idlecars import client_side_routes

import forms
import models
import jobs


'''
View that presents the landing page and a 'subscribe' forms for Drivers and Owners.
There are two forms on the page, each of which has a different 'action' url. The two
actions are both handled through this view.
'''
def index(request):
    context = {
        'login_url': client_side_routes.driver_account(),
        'terms_of_service': client_side_routes.terms_of_service(),
        'faq': client_side_routes.faq(),
        'add_car_form': client_side_routes.add_car_form(),
    }
    return render(request, 'landing_page.jade', context)


'''
View that presents the about page
'''
def about(request):
    context = {}
    return render(request, 'about_page.jade', context)


'''
View to handle the driver survey form, store form info and respond with a thank you message.
'''
def driver_survey(request, pk=None):
    if request.method == 'POST':
        survey_form = forms.DriverSurveyForm(request.POST)
        if survey_form.is_valid():
            survey = survey_form.save(commit=False)
            contact = get_object_or_404(models.Contact, pk=pk)
            survey.contact = contact
            survey.save()

            url = '{}?thanks='.format(urlresolvers.reverse('website:index'))
            return HttpResponseRedirect(url)
    else:
        survey_form = forms.DriverSurveyForm(initial={'exchange': '_no_response'})

    # if it was a GET request, or if there isn't valid form data...
    context = {
        'action': urlresolvers.reverse('website:driver_survey', args=(pk,)),
        'survey_form': survey_form,
    }
    return render(request, 'driver_survey.jade', context)


'''
View to handle the owner survey form, store form info and respond with a thank you message.
'''
def owner_survey(request, pk=None):
    if request.method == 'POST':
        survey_form = forms.OwnerSurveyForm(request.POST)
        if survey_form.is_valid():
            survey = survey_form.save(commit=False)
            contact = get_object_or_404(models.Contact, pk=pk)
            survey.contact = contact
            survey.save()

            url = '{}?thanks='.format(urlresolvers.reverse('website:index'))
            return HttpResponseRedirect(url)
    else:
        survey_form = forms.OwnerSurveyForm()

    # if it was a GET request, or if there isn't valid form data...
    context = {
        'action': urlresolvers.reverse('website:owner_survey', args=(pk,)),
        'survey_form': survey_form,
    }
    return render(request, 'owner_survey.jade', context)
