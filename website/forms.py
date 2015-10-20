# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django import forms

import models


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
            'account_groundlink',
            'account_other',
            'account_other_name',
            'car_owner',
            'vehicle_type',
            'shift_choice',
            'shift_other_start',
            'shift_other_end',
            'exchange',
        ]
        widgets = {
            'exchange': forms.RadioSelect(),
        }

class OwnerSurveyForm(forms.ModelForm):
    class Meta:
        model = models.OwnerSurvey
        fields = ['source', 'other_source']
