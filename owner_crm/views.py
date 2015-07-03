# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import mandrill

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, Http404
from rest_framework import viewsets, mixins

from tests import sample_merge_vars
import serializers, models


class UpdateRenewalView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.Renewal.objects.all()
    serializer_class = serializers.Renewal
    lookup_field = 'token'


def email_preview(request, pk):
    if not pk in sample_merge_vars.merge_vars:
        raise Http404('That email template doesn\'t exist.')

    client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
    merge_vars = sample_merge_vars.merge_vars[pk]

    # format the merge_vars for this API call
    pairs = merge_vars[merge_vars.keys()[0]]
    template_content = [{"name": k, "content": v} for k, v in pairs.iteritems()]
    rendered = client.templates.render(pk, [], merge_vars=template_content)
    return HttpResponse(rendered['html'])
