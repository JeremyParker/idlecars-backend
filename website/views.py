# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.core import urlresolvers

from django.http import HttpResponse, HttpResponseRedirect

import forms
import models


'''
View that presents the landing page and a 'subscribe' forms for Drivers and Owners.
There are two forms on the page, each of which has a different 'action' url. The two
actions are both handled through this view.
'''
def index(request):
    prospect_form = forms.ProspectForm()

    if request.method == 'POST':
        prospect_form = forms.ProspectForm(request.POST or None)
        if prospect_form.is_valid():
            new_prospect = prospect_form.save()
            if new_prospect.role == "driver":
                return HttpResponseRedirect(urlresolvers.reverse('website:driver_survey', args=(new_prospect.pk,)))
            else:
                return HttpResponseRedirect(urlresolvers.reverse('website:owner_survey', args=(new_prospect.pk,)))

    # if it was a GET request, or if there isn't valid form data...
    context = {
        'action': urlresolvers.reverse('website:index'),
        'prospect_form': prospect_form,
    }
    return render(request, 'landing_page.jade', context)


'''
View to handle the driver survey form, store form info and respond with a thank you message.
'''
def driver_survey(request, pk=None):
    survey_form = forms.DriverSurveyForm(request.POST or None)
    if request.method == 'POST':
        if survey_form.is_valid():
            survey = survey_form.save(commit=False)
            prospect = get_object_or_404(models.Prospect, pk=pk)
            survey.prospect = prospect
            survey.save()
            return HttpResponseRedirect(urlresolvers.reverse('website:thankyou'))

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
    survey_form = forms.OwnerSurveyForm(request.POST or None)
    if request.method == 'POST':
        if survey_form.is_valid():
            survey = survey_form.save(commit=False)
            prospect = get_object_or_404(models.Prospect, pk=pk)
            survey.prospect = prospect
            survey.save()
            return HttpResponseRedirect(urlresolvers.reverse('website:thankyou'))

    # if it was a GET request, or if there isn't valid form data...
    context = {
        'action': urlresolvers.reverse('website:owner_survey', args=(pk,)),
        'survey_form': survey_form,
    }
    return render(request, 'owner_survey.jade', context)


'''
A final thankyou for submitting the extra market survey info.
'''
def thankyou(request):
    return HttpResponse("Thankyou for taking the time to fill out our survey. Someone will be in touch shortly.")
