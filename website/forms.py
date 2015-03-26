# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django import forms

import models

class ProspectForm(forms.ModelForm):
    class Meta:
        model = models.Prospect
        exclude = []

class DriverSurveyForm(forms.ModelForm):
    class Meta:
        model = models.DriverSurvey
        exclude = ['prospect']        

class OwnerSurveyForm(forms.ModelForm):
    class Meta:
        model = models.OwnerSurvey
        exclude = ['prospect']
