# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.conf import settings

from rest_framework.routers import DefaultRouter

class OptionalApiRootDefaultRouter(DefaultRouter):
    '''
    This class doesn't provide a root-api view if BrowsableAPIRenderer isn't in the renderers
    '''
    def __init__(self, *args, **kwargs):
        super(OptionalApiRootDefaultRouter, self).__init__(*args, **kwargs)
        renderers_conf = settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']
        if 'rest_framework.renderers.BrowsableAPIRenderer' not in renderers_conf:
            self.include_root_view = False
