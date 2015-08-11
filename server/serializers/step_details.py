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
        'step_subtitle': "Your insurance has been approved. Pick up your car!",
    },
    5: {
        'step_title': 'Rental in progress',
        'step_subtitle': 'Trouble with your car? Call idlecars: (844) 435-3227',
    }
}

def get_step_details(booking):
    ret = step_details[booking_state.get_step(booking.state)]
    if booking.state == Booking.REQUESTED:
        ret.update({
            'step_subtitle': 'As soon as you are approved on the insurance you can pick up your car',
        })
    return ret
