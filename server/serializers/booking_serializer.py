# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal

from django.utils import timezone
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from idlecars import fields
from server.models import Car, Booking, Driver, Payment
from server.services import booking as booking_service
from server.services import invoice_service
from server.services import car as car_service
from server.serializers import listing_serializer, payment_serializer


class BookingSerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())
    driver = serializers.ReadOnlyField(source='driver.pk')

    class Meta:
        model = Booking
        fields = ('id', 'car', 'driver')
        read_only_fields = ('id', 'driver')

    def is_valid(self, raise_exception=False):
        valid = super(BookingSerializer, self).is_valid(raise_exception=raise_exception)
        if not valid:
            return valid

        if self.context['request'].method == 'POST':
            car_pk = int(self.initial_data['car'])
            live_car_pks = [c.pk for c in car_service.filter_live(Car.objects.all())]
            if not car_pk in live_car_pks:
                self._errors.update({
                    '_app_notifications': [booking_service.UNAVAILABLE_CAR_ERROR],
                })

            # TODO(JP): make this aware of end-times, so we can book after a booking ends
            driver = Driver.objects.get(auth_user=self.context['request'].user)
            if booking_service.filter_visible(Booking.objects.filter(driver=driver)):
                self._errors.update({
                    '_app_notifications': ['You have a conflicting rental.'],
                })

        if self._errors and raise_exception:
            raise ValidationError(self._errors)

        return not bool(self._errors)

    def create(self, validated_data):
        car = validated_data['car']
        driver = validated_data['driver']
        return booking_service.create_booking(car, driver)


class BookingDetailsSerializer(serializers.ModelSerializer):
    car = serializers.SerializerMethodField()
    next_payment = serializers.SerializerMethodField()
    start_time_display = serializers.SerializerMethodField()
    start_time_estimated = serializers.SerializerMethodField()
    end_time_display = serializers.SerializerMethodField()
    end_time = fields.DateArrayField()
    first_valid_end_time = serializers.SerializerMethodField()
    end_time_limit_display = serializers.SerializerMethodField()
    step = serializers.SerializerMethodField()
    step_display_count = serializers.SerializerMethodField()
    step_details = serializers.SerializerMethodField()
    paid_payments = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'id',
            'car',
            'step',
            'step_display_count',
            'step_details',
            'next_payment',
            'start_time_display',
            'start_time_estimated',
            'end_time_display',
            'end_time',
            'first_valid_end_time',
            'end_time_limit_display',
            'paid_payments',
        )
        read_only_fields = (
            'id',
            'car',
            'step',
            'step_display_count',
            'step_details',
            'next_payment',
            'start_time_display',
            'start_time_estimated',
            'end_time_display',
            'first_valid_end_time',
            'end_time_limit_display',
            'paid_payments',
        )

    def update(self, instance, validated_data):
        '''
        We can change the end_time.
        '''
        if 'end_time' in validated_data:
            return booking_service.set_end_time(instance, validated_data['end_time'])
        return instance

    def get_car(self, obj):
        # if the booking is in the RETURNED state, use a custom serializer with contact info
        if obj.get_state() == Booking.RETURNED:
            serializer = listing_serializer.ListingPickupSerializer
        else:
            serializer = listing_serializer.ListingSerializer
        return serializer(obj.car).data

    def get_step(self, obj):
        state = obj.get_state()
        if state == Booking.RETURNED:
            return 4
        elif state in [Booking.REQUESTED]:
            return 3
        elif state == Booking.PENDING:
            return 2
        return None

    def get_step_display_count(self, obj):
        return 3

    def get_step_details(self, obj):
        if not booking_service.is_visible(obj):
            return None
        step_details = {
            2: {
                'step_title': 'Create your account',
                'step_subtitle': 'You must upload your documents to rent this car',
            },
            3: {
                'step_title': 'Your request has been submitted',
                'step_subtitle': "The owner will contact you when you are approved and added to the car.",
            },
            4: {
                'step_title': 'Rental in progress',
                'step_subtitle': 'You have been added to your car',
            }
        }
        step = self.get_step(obj)
        ret = step_details[step]
        return ret

    def get_next_payment(self,obj):
        # if obj.get_state() == Booking.ACTIVE:
        #     fee, amount, credit_amount, start_time, end_time = invoice_service.calculate_next_rent_payment(obj)
        # else:
        #     fee, amount, credit_amount, start_time, end_time = booking_service.estimate_next_rent_payment(obj)
        # if start_time:
        #     start_time = start_time.strftime('%b %d')
        return {'amount': Decimal('0.00'), 'start_time': None, 'credit': Decimal('0.00')}

    def get_start_time_display(self, obj):
        return booking_service.start_time_display(obj)

    def get_start_time_estimated(self, obj):
        return not obj.approval_time

    def get_first_valid_end_time(self, obj):
        first_valid_end, _ = booking_service.first_valid_end_time(obj)
        return fields.format_date_array(first_valid_end)

    def get_end_time_limit_display(self, obj):
        ''' determine if we should show the min rental period, or the one week notice limit '''
        _, min_rental_still_limiting = booking_service.first_valid_end_time(obj)
        if min_rental_still_limiting:
            return '{} minimum'.format(Car.MIN_LEASE_CHOICES[obj.car.min_lease])
        else:
            return '7 days notice'

    def get_end_time_display(self, booking):
        def _format_date(date):
            return date.strftime('%b %d')

        if booking.approval_time:
            return _format_date(booking.approval_time)
        else:
            return 'Not approved'

    def get_paid_payments(self, booking):
        paid_payments = booking.payment_set.filter(status=Payment.SETTLED)
        return [payment_serializer.PaymentSerializer(p).data for p in paid_payments]
