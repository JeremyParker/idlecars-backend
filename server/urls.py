# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.core.urlresolvers import NoReverseMatch

from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.compat import get_resolver_match, OrderedDict
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

import views


class PrivateBrowsableDefaultRouter(DefaultRouter):
    def get_api_root_view(self):
        """
        Return a view to use as the API root.
        """
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        class APIRoot(APIView):
            permission_classes = (IsAdminUser,)
            _ignore_model_permissions = True

            def get(self, request, *args, **kwargs):
                ret = OrderedDict()
                namespace = get_resolver_match(request).namespace
                for key, url_name in api_root_dict.items():
                    if namespace:
                        url_name = namespace + ':' + url_name
                    try:
                        ret[key] = reverse(
                            url_name,
                            request=request,
                            format=kwargs.get('format', None)
                        )
                    except NoReverseMatch:
                        # Don't bail out if eg. no list routes exist, only detail routes.
                        continue

                return Response(ret)

        return APIRoot.as_view()


router = PrivateBrowsableDefaultRouter()
router.register(r'cars', views.CarViewSet, base_name='cars')
router.register(r'bookings', views.CreateBookingView, base_name='bookings')


urlpatterns = [
    url(r'^', include(router.urls)),
]
