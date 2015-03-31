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

    def _show_thanks():
        return 'thanks' in request.GET

    if request.method == 'POST':
        contact_form = forms.ContactForm(request.POST)
        if contact_form.is_valid():
            try:
                new_contact = models.Contact.objects.get(email=contact_form.cleaned_data['email'])
            except models.Contact.DoesNotExist:
                new_contact = contact_form.save()

            if new_contact.role == 'driver':
                jobs.queue_driver_welcome_email(new_contact.email)
            else:
                jobs.queue_owner_welcome_email(new_contact.email)

            # NOTE(jefk): survey is not ready yet, so now redirect to home
            url = '{}?thanks='.format(urlresolvers.reverse('website:index'))
            return HttpResponseRedirect(url)
            # if new_contact.role == "driver":
            #     return HttpResponseRedirect(urlresolvers.reverse('website:driver_survey', args=(new_contact.pk,)))
            # else:
            #     return HttpResponseRedirect(urlresolvers.reverse('website:owner_survey', args=(new_contact.pk,)))
    else:
        contact_form = forms.ContactForm()


    # if it was a GET request, or if there isn't valid form data...
    context = {
        'action': urlresolvers.reverse('website:index'),
        'contact_form': contact_form,
        'show_thanks': _show_thanks(),
    }
    return render(request, 'landing_page.jade', context)


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

def email_preview(request):
    return render(request, 'owner_welcome_email.html')
