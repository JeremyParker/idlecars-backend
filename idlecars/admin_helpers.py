# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import django.utils
from django.core import urlresolvers


# helper to make links on admin pages
def link(obj, text=None):
    if text is None:
        text = unicode(obj)
    if obj.pk:
        view = "admin:{0}_{1}_change".format(obj._meta.app_label, obj._meta.model_name)
        view_url = urlresolvers.reverse(view, args=(obj.pk,))
    else:
        view = "admin:{0}_{1}_add".format(obj._meta.app_label, obj._meta.model_name)
        view_url = urlresolvers.reverse(view, args=())
    a_str = '<a href="{view_url}">{text}</a>'.format(view_url=view_url, text=text)
    return django.utils.safestring.mark_safe(a_str)
