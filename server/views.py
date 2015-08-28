# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework import status

from idlecars import fields
from owner_crm.services import password_reset_service

import models, services
from services import auth_user as auth_user_service
from serializers import CarSerializer, BookingSerializer, BookingDetailsSerializer
from serializers import DriverSerializer, PhoneNumberSerializer
from permissions import OwnsDriver, OwnsBooking
from server.models import Owner
from server.services import owner_bank_link_service
from server.permissions import OwnsOwner


class CarViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = services.car.listing_queryset.order_by('solo_cost')
    serializer_class = CarSerializer


class BookingViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'partial_update']:
            return BookingDetailsSerializer
        return BookingSerializer

    def get_permissions(self):
        return (IsAuthenticated() if self.request.method == 'POST' else OwnsBooking()),

    def perform_create(self, serializer):
        driver = models.Driver.objects.get(auth_user=self.request.user)
        serializer.save(driver=driver)

    def get_queryset(self):
        return models.Booking.objects.filter(
            driver=models.Driver.objects.get(auth_user=self.request.user),
            state__in=services.booking.visible_states
        )


class DriverViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
    ):
    serializer_class = DriverSerializer
    model = models.Driver
    queryset = models.Driver.objects.all()

    def get_permissions(self):
        # allow non-authenticated user to create a Driver
        return (AllowAny() if self.request.method == 'POST' else OwnsDriver()),

    def get_object(self):
        ''' override to map 'me' to the current user's driver object '''
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.request.user.is_authenticated() and self.kwargs[lookup_url_kwarg] == 'me':
            try:
                self.kwargs[lookup_url_kwarg] = models.Driver.objects.get(auth_user=self.request.user).pk
            except models.Driver.DoesNotExist:
                raise Http404
        return super(DriverViewSet, self).get_object()


class OwnerViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet
    ):
    queryset = Owner.objects.all()

    @detail_route(methods=['post'], permission_classes=[OwnsOwner])
    def bank_link(self, request, pk=None):
        owner = self.get_object()
        result = owner_bank_link_service.link(owner, request.data)

        if not result.get('error'):
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberDetailView(APIView):
    def get(self, request, pk, format=None):
        phone_number = fields.parse_phone_number(pk)
        try:
            auth_user = User.objects.get(username=phone_number)
            serializer = PhoneNumberSerializer(auth_user)
            return Response(serializer.data)

        except User.DoesNotExist:
            # If an old-skool UserAccount exists, and an Owner exists then it's an owner signing up.
            user_accounts = models.UserAccount.objects.filter(phone_number=phone_number)
            if not [u.owner for u in user_accounts if u.owner]:
                raise Http404

            # we can only have one auth.User per phone. Use the first.
            auth_user = auth_user_service.create_auth_user(user_accounts[0])
            user_accounts[0].owner.auth_user.add(auth_user)
            password_reset_service.invite_owner(auth_user)

            content = PhoneNumberSerializer(auth_user).data
            content.update({'_app_notifications': [
                '''
                Great, you're in our system already! An email has been sent to your address
                with instructions for setting your password.
                '''
            ],})
            return Response(content)
