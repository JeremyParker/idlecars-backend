# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from . import Booking


states = {
    Booking.PENDING: {
        'visible': True,
        'cancelable': True,
        'details': {
            "status": "Waiting for documents",
            "content": "You must upload your documents to rent this car.",
            "color": "rgb(255,51,51)",
        },
        'step_details': {
            'step': 2,
        }
    },
    Booking.COMPLETE: {
        'visible': True,
        'cancelable': True,
        'details': {
            "status": "Documents uploaded",
            "content": "Your documents are being reviewed.",
            "color": "rgb(255,128,0)"
        },
        'step_details': {
            'step': 3,
        }
    },
    Booking.REQUESTED: {
        'visible': True,
        'cancelable': True,
        'details': {
            "status": "Insurance processing",
            "content": "You are being added to this car's insurance.",
            "color": "rgb(255,128,0)"
        },
        'step_details': {
            'step': 4,
        }
    },
    Booking.ACCEPTED: {
        'visible': True,
        'cancelable': False,
        'details': {
            "status": "Ready for pickup",
            "content": "Please call us if you need assistance. 1-844-435-3227",
            "color": "rgb(255,51,51)"
        },
        'step_details': {
            'step': 4,
        }
    },
    Booking.BOOKED: {
        'visible': True,
        'cancelable': False,
        'details': {
            "status": "In progress",
            "content": "Happy driving!",
            "color": "rgb(0,204,0)"
        },
        'step_details': {
            'step': 5,
        }
    },
    Booking.FLAKE: {
        'visible': True,
        'cancelable': True,
        'details': {
            "status": "Waiting for documents",
            "content": "Please upload your driver documents.",
            "color": "rgb(255,51,51)"
        },
        'step_details': {
            'step': 2,
        }
    },
    Booking.TOO_SLOW: {
        'visible': False,
        'cancelable': False,
    },
    Booking.OWNER_REJECTED: {
        'visible': False,
        'cancelable': False,
    },
    Booking.DRIVER_REJECTED: {
        'visible': False,
        'cancelable': False,
    },
    Booking.MISSED: {
        'visible': False,
        'cancelable': False,
    },
    Booking.TEST_BOOKING: {
        'visible': False,
        'cancelable': False,
    },
    Booking.CANCELED: {
        'visible': False,
        'cancelable': False,
    },
}


def visible_states():
    return [s for s in states.keys() if states[s]['visible']]

def cancelable_states():
    return [s for s in states.keys() if states[s]['cancelable']]
