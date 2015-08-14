# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from idlecars import fields
from server.models import Car, Booking, Driver, booking_state
from server.services import booking as booking_service
from server.services import car as car_service
from server.serializers import car_serializer


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

        # TODO(JP): make this booking-check aware of end-times, so we can book after booking ends.
        if self.context['request'].method == 'POST':
            driver = Driver.objects.get(auth_user=self.context['request'].user)
            if Booking.objects.filter(driver=driver, state__in=range(Booking.FLAKE + 1)):
                self._errors.update({
                    '_app_notifications': ['You have a conflicting rental.'],
                })

        # TODO(JP): double-check the car is available

        if self._errors and raise_exception:
            raise ValidationError(self._errors)

        return not bool(self._errors)

    def create(self, validated_data):
        car = validated_data['car']
        driver = validated_data['driver']
        return booking_service.create_booking(car, driver)


class BookingDetailsSerializer(serializers.ModelSerializer):
    car = serializers.SerializerMethodField()
    state_details = serializers.SerializerMethodField()
    start_time_display = serializers.SerializerMethodField()
    start_time_estimated = serializers.SerializerMethodField()
    end_time_display = serializers.SerializerMethodField()
    end_time = fields.DateArrayField()
    first_valid_end_time = serializers.SerializerMethodField()
    end_time_limit_display = serializers.SerializerMethodField()
    step = serializers.SerializerMethodField()
    step_display_count = serializers.SerializerMethodField()

    step_details = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'id',
            'car',
            'state',
            'state_details',
            'step',
            'step_display_count',
            'step_details',
            'start_time_display',
            'start_time_estimated',
            'end_time_display',
            'end_time',
            'first_valid_end_time',
            'end_time_limit_display',
        )
        read_only_fields = (
            'id',
            'car',
            'state_details',
            'step',
            'step_display_count',
            'step_details',
            'start_time_display',
            'start_time_estimated',
            'end_time_display',
            'first_valid_end_time',
            'end_time_limit_display',
        )

    def update(self, instance, validated_data):
        '''
        We can change the end_time. Changing state is deprecated
        '''
        if 'state' in validated_data:
            if validated_data['state'] == Booking.CANCELED:
                if instance.state not in booking_state.cancelable_states():
                    raise ValidationError('This rental can\'t be canceled at this time.')
                return booking_service.cancel(instance)

            raise ValidationError('This is not a valid state for a rental.')

        if 'end_time' in validated_data:
            return booking_service.set_end_time(instance, validated_data['end_time'])

        return instance

    def get_car(self, obj):
        # if the booking is in the ACCEPTED state, use a custom serializer with contact info
        if obj.state == Booking.ACCEPTED:
            serializer = car_serializer.CarPickupSerializer
        else:
            serializer = car_serializer.CarSerializer
        return serializer(obj.car).data

    def get_state_details(self, obj):
        if not booking_state.state[obj.state]['visible']:
            return None
        deets = booking_state.state[obj.state]['details']
        deets.update({"cancelable": obj.state in booking_state.cancelable_states()})
        return deets

    def get_step(self, obj):
        if obj.state == Booking.PENDING or obj.state == Booking.FLAKE:
            if obj.checkout_time:
                return 4
            elif obj.driver.all_docs_uploaded():
                return 3
            else:
                return 2
        elif obj.state == Booking.REQUESTED or obj.state == Booking.ACCEPTED:
            return 4
        elif obj.state == Booking.BOOKED:
            return 5
        return None

    def get_step_display_count(self, obj):
        return 4

    def get_step_details(self, obj):
        if not booking_state.state[obj.state]['visible']:
            return None
        step_details = {
            2: {
                'step_title': 'Create your account',
                'step_subtitle': 'You must upload your documents to rent this car',
            },
            3: {
                'step_title': 'Reserve your car',
                'step_subtitle': 'Put down the deposit to reserve your car',
            },
            4: {
                'step_title': 'Pick up your car',
                'step_subtitle': "Your insurance has been approved. Pick up your car!",
            },
            5: {
                'step_title': 'Rental in progress',
                'step_subtitle': 'Trouble with your car? Call idlecars: (844) 435-3227',
            }
        }
        step = self.get_step(obj)
        ret = step_details[step]

        # differentiate between step 4 requested, and step 4 ready for pickup
        if 4 == step and obj.state and not obj.state == Booking.ACCEPTED:
            ret.update({
                'step_subtitle': 'As soon as you are approved on the insurance you can pick up your car',
            })
        return ret

    def get_start_time_display(self, obj):
        return booking_service.start_time_display(obj)

    def get_start_time_estimated(self, obj):
        return not obj.approval_time

    def get_first_valid_end_time(self, obj):
        first_end = booking_service.first_valid_end_time(obj)
        return fields.format_date_array(first_end)

    def get_end_time_limit_display(self, obj):
        ''' determine if we should show the min rental period, or the one week notice limit '''
        if booking_service.min_rental_still_limiting(obj):
            return '{} minimum'.format(Car.MIN_LEASE_CHOICES[obj.car.min_lease])
        else:
            return '7 days notice'

    def get_end_time_display(self, booking):
        def _format_date(date):
            return date.strftime('%b %d')

        min_duration = car_service.get_min_rental_duration(booking.car)
        if booking.end_time:
            return _format_date(booking.end_time)
        elif booking.approval_time:
            time_string = _format_date(booking.approval_time + datetime.timedelta(days=min_duration + 1))
        elif booking.checkout_time:
            time_string = _format_date(booking.checkout_time + datetime.timedelta(days=min_duration + 2))
        else:
            time_string = _format_date(timezone.now() + datetime.timedelta(days=min_duration + 2))

        return time_string
