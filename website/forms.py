# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django import forms

import models

class ContactForm(forms.ModelForm):
    class Meta:
        model = models.Contact
        fields = ['email', 'zipcode', 'role']
        widgets = {
            'role': forms.RadioSelect(),
        }


class DriverSurveyForm(forms.ModelForm):
    class Meta:
        model = models.DriverSurvey
        fields = [
            'source',
            'other_source',
            'licenced',
            'credit_card',
            'account_uber',
            'account_lyft',
            'account_whisk',
            'account_via',
            'account_gett',
            'account_other',
            'account_other_name',
            'exchange',
            'car_owner',
            'vehicle_type',
            'rent_monday',
            'rent_tuesday',
            'rent_wednesday',
            'rent_thursday',
            'rent_friday',
            'rent_saturday',
            'rent_sunday',
            'start_monday',
            'start_tuesday',
            'start_wednesday',
            'start_thursday',
            'start_friday',
            'start_saturday',
            'start_sunday',
            'end_monday',
            'end_tuesday',
            'end_wednesday',
            'end_thursday',
            'end_friday',
            'end_friday',
            'end_saturday',
            'end_sunday',
        ]
        widgets = {
            'exchange': forms.RadioSelect(),
        }

class OwnerSurveyForm(forms.ModelForm):
    class Meta:
        model = models.OwnerSurvey
        fields = ['source', 'other_source']        
