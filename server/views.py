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
from services import owner_service
from serializers import CarSerializer, BookingSerializer, BookingDetailsSerializer
from serializers import DriverSerializer, OwnerSerializer, PhoneNumberSerializer
from permissions import OwnsDriver, OwnsBooking
from models import Owner
from permissions import OwnsOwner


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
    model = models.Owner
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer
    permission_classes = (OwnsOwner,)

    def get_object(self):
        ''' override to map 'me' to the current user's driver object '''
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if self.request.user.is_authenticated() and self.kwargs[lookup_url_kwarg] == 'me':
            try:
                self.kwargs[lookup_url_kwarg] = models.Owner.objects.get(auth_users=self.request.user).pk
            except models.Owner.DoesNotExist:
                raise Http404
        return super(OwnerViewSet, self).get_object()

    @detail_route(methods=['post'], permission_classes=[OwnsOwner])
    def bank_link(self, request, pk=None):
        owner = self.get_object()
        error_fields, error_msg = owner_service.link_bank_account(owner, request.data)

        if not error_msg:
            return Response({}, status=status.HTTP_201_CREATED)
        else:
            data = {
                'error_fields': error_fields,
                '_app_notifications': error_msg
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberDetailView(APIView):
    def get(self, request, pk, format=None):
        try:
            driver = models.Driver.objects.get(auth_user__username=fields.parse_phone_number(pk))
        except models.Driver.DoesNotExist:
            # TODO(JP) create a new Driver, call start_set_password(auth_user).
            raise Http404

        serializer = PhoneNumberSerializer(driver.auth_user, many=False)
        return Response(serializer.data)


class OwnerPhoneNumberDetailView(APIView):
    def get(self, request, pk, format=None):
        phone_number = fields.parse_phone_number(pk)
        try:
            created, auth_user = owner_service.invite_legacy_owner(phone_number)
        except Owner.DoesNotExist:
            content = {'_app_notifications': [
                '''
                Sorry, something went wrong. We couldn't find a record of you as a car-owner
                in our system. Please contact idlecars, to set up your owner account.
                '''
            ],}
            return Response(content, status.HTTP_404_NOT_FOUND)

        if created:
            content = PhoneNumberSerializer(auth_user).data
            content.update({'_app_notifications': [
                '''
                Great, you're in our system already! An email has been sent to your address
                with instructions for setting your password.
                '''
            ],})
            return Response(content, status.HTTP_404_NOT_FOUND)
        else:
            serializer = PhoneNumberSerializer(auth_user)
            return Response(serializer.data, status.HTTP_200_OK)
