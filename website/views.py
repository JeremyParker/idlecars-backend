# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect

import forms
import models
import jobs


'''
View that presents the landing page and a 'subscribe' forms for Drivers and Owners.
There are two forms on the page, each of which has a different 'action' url. The two
actions are both handled through this view.
'''
def index(request):
    contact_form = forms.ContactForm()

    if request.method == 'POST':
        contact_form = forms.ContactForm(request.POST or None)
        if contact_form.is_valid():
            new_contact = contact_form.save()
            jobs.queue_welcome_email(new_contact.email)

            # NOTE(jefk): survey is not ready yet, so now redirect to home
            # if new_contact.role == "driver":
            #     return HttpResponseRedirect(urlresolvers.reverse('website:driver_survey', args=(new_contact.pk,)))
            # else:
            #     return HttpResponseRedirect(urlresolvers.reverse('website:owner_survey', args=(new_contact.pk,)))

    # if it was a GET request, or if there isn't valid form data...
    context = {
        'action': urlresolvers.reverse('website:index'),
        'contact_form': contact_form,
        'show_thanks': True,
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
            contact = get_object_or_404(models.Contact, pk=pk)
            survey.contact = contact
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
            contact = get_object_or_404(models.Contact, pk=pk)
            survey.contact = contact
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
