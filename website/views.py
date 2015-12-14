# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.core import urlresolvers
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings

from idlecars import app_routes_driver, app_routes_owner

import forms
import models
import jobs


'''
View that presents the landing page for Drivers and Owners.
'''
def index(request):
    context = {
        'login_url': app_routes_driver.driver_login(),
        'signup_url': app_routes_driver.driver_signup(),
        'terms_of_service': app_routes_driver.terms_of_service(),
        'faq': app_routes_driver.faq(),
        'owner_app_url': app_routes_owner.owner_app_url(),
    }
    return render(request, 'landing_page.jade', context)


'''
View that presents the about page
'''
def about(request):

    def show_thanks():
        return 'thanks' in request.GET

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        new_message = models.UserMessage.objects.create(
            first_name=first_name,
            email=email,
            message=message,
        )

        from owner_crm.services import notification
        notification.send('ops_notifications.NewUserMessage', new_message)

        url = '{}?thanks='.format(urlresolvers.reverse('website:about'))
        return HttpResponseRedirect(url)

    context = {
        'login_url': app_routes_driver.driver_account(),
        'signup_url': app_routes_driver.driver_signup(),
        'terms_of_service': app_routes_driver.terms_of_service(),
        'faq': app_routes_driver.faq(),
        'owner_app_url': app_routes_owner.owner_app_url(),
        'action': urlresolvers.reverse('website:about') + '#thanks',
        'show_thanks': show_thanks(),
    }
    return render(request, 'about_page.jade', context)


'''
View that redirects users to driver sign up page
'''
def driver_referral(request, credit=None):
    if credit != '50' and credit != '75':
        return HttpResponseNotFound('Sorry, this page is not found')

    utm = '?utm_campaign=referral&utm_medium=fliers&utm_source=-&utm_content=' + credit
    url = app_routes_driver.driver_signup() + utm
    return HttpResponseRedirect(url)


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
