# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django import forms

import models

class DriverProspectForm(forms.ModelForm):
    class Meta:
        model = models.DriverProspect

