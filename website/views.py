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
    driver_form = forms.DriverProspectForm()
    owner_form = forms.OwnerProspectForm()

    if request.method == 'POST':
        if request.path_info == urlresolvers.reverse('driver_endpoint'):
            driver_form = forms.DriverProspectForm(request.POST or None)
            if driver_form.is_valid():
                new_driver = driver_form.save()
                return HttpResponseRedirect(urlresolvers.reverse('driver_survey', args=(new_driver.pk,)))

        elif request.path_info == urlresolvers.reverse('owner_endpoint'):
            owner_form = forms.OwnerProspectForm(request.POST or None)
            if owner_form.is_valid():
                new_owner = owner_form.save()
                return HttpResponseRedirect(urlresolvers.reverse('owner_survey', args=(new_owner.pk,)))

    # if it was a GET request, or if there isn't valid form data...
    context = {
        'driver_action': urlresolvers.reverse('driver_endpoint'),
        'driver_form': driver_form,
        'owner_action': urlresolvers.reverse('owner_endpoint'),
        'owner_form': owner_form,
    }
    return render(request, 'landing_page.jade', context)


'''
View to handle the driver survey form, store form info and respond with a thank you message.
'''
def driver_survey(request, driver_pk=None):
    new_driver = get_object_or_404(models.DriverProspect, pk=driver_pk)
    survey_form = forms.DriverSurveyForm(request.POST or None)

    if request.method == 'POST':
        if survey_form.is_valid():
            survey_form.save()
            return HttpResponseRedirect(urlresolvers.reverse('thankyou'))

    # if it was a GET request, or if there isn't valid form data...
    context = {
        'action': urlresolvers.reverse('driver_survey', args=(new_driver.pk,)),
        'survey_form': survey_form,
    }
    return render(request, 'driver_survey.jade', context)


'''
View to handle the owner survey form, store form info and respond with a thank you message.
'''
def owner_survey(request, owner_pk=None):
    new_owner = get_object_or_404(models.OwnerProspect, pk=owner_pk)
    survey_form = forms.OwnerSurveyForm(request.POST or None)

    if request.method == 'POST':
        if survey_form.is_valid():
            survey_form.save()
            return HttpResponseRedirect(urlresolvers.reverse('thankyou'))

    # if it was a GET request, or if there isn't valid form data...
    context = {
        'action': urlresolvers.reverse('owner_survey', args=(new_owner.pk,)),
        'survey_form': survey_form,
    }
    return render(request, 'owner_survey.jade', context)


'''
A final thankyou for submitting the extra market survey info.
'''
def thankyou(request):
    return HttpResponse("Thankyou for taking the time to fill out our survey. Someone will be in touch shortly.")
