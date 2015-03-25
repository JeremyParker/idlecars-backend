# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django import forms

import models

class DriverProspectForm(forms.ModelForm):
    class Meta:
        model = models.DriverProspect

class OwnerProspectForm(forms.ModelForm):
    class Meta:
        model = models.OwnerProspect

class DriverSurveyForm(forms.ModelForm):
    class Meta:
        model = models.DriverSurvey

class OwnerSurveyForm(forms.ModelForm):
    class Meta:
        model = models.OwnerSurvey