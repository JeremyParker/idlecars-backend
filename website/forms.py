# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django import forms

import models

class ContactForm(forms.ModelForm):
    class Meta:
        model = models.Contact
        fields = ['role', 'email', 'zipcode']
        widgets = {
            'role': forms.RadioSelect(),
        }


class DriverSurveyForm(forms.ModelForm):
    class Meta:
        model = models.DriverSurvey
        fields = ['source', 'other_source']

class OwnerSurveyForm(forms.ModelForm):
    class Meta:
        model = models.OwnerSurvey
        fields = ['source', 'other_source']
