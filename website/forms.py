# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django import forms

import models

class ContactForm(forms.ModelForm):
    class Meta:
        model = models.Contact
        exclude = []

class DriverSurveyForm(forms.ModelForm):
    class Meta:
        model = models.DriverSurvey
        exclude = ['contact']        

class OwnerSurveyForm(forms.ModelForm):
    class Meta:
        model = models.OwnerSurvey
        exclude = ['contact']
