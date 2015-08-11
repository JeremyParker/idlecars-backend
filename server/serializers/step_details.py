# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.models import Booking, booking_state

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
        'step_subtitle': "Once you're on the insurance, you can pick up your car",
    },
    5: {
        'step_title': 'Rental in progress',
        'step_subtitle': 'If you have any trouble with your car, please call idlecars',
    }
}

def get_step_details(booking):
    ret = step_details[booking_state.get_step(booking.state)]
    if booking.state == Booking.REQUESTED:
        ret.update({
            'step_subtitle': 'You have been added to the insurance. You can now pick up your car',
        })
    return ret
