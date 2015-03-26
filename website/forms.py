# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django import forms

import models

class DriverProspectForm(forms.ModelForm):
    class Meta:
        model = models.DriverProspect
        exclude = []

class OwnerProspectForm(forms.ModelForm):
    class Meta:
        model = models.OwnerProspect
        exclude = []

class DriverSurveyForm(forms.ModelForm):
    class Meta:
        model = models.DriverSurvey
        exclude = ['driver_prospect']        

class OwnerSurveyForm(forms.ModelForm):
    class Meta:
        model = models.OwnerSurvey
        exclude = ['owner_prospect']
