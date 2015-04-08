# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html')),
]
