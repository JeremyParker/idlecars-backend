# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from . import Booking


state = {
    Booking.PENDING: {
        'visible': True,
        'cancelable': True,
        'checkoutable': True,
        'pickupable': False,
        'details': {
            "status": "Waiting for documents",
            "content": "You must upload your documents to rent this car.",
            "color": "rgb(255,51,51)",
        },
    },
    Booking.REQUESTED: {
        'visible': True,
        'cancelable': True,
        'checkoutable': False,
        'pickupable': False,
        'details': {
            "status": "Insurance processing",
            "content": "You are being added to this car's insurance.",
            "color": "rgb(255,128,0)"
        },
    },
    Booking.ACCEPTED: {
        'visible': True,
        'cancelable': False,
        'checkoutable': False,
        'pickupable': True,
        'details': {
            "status": "Ready for pickup",
            "content": "Please call us if you need assistance. 1-844-435-3227",
            "color": "rgb(255,51,51)"
        },
    },
    Booking.BOOKED: {
        'visible': True,
        'cancelable': False,
        'checkoutable': False,
        'pickupable': False,
        'details': {
            "status": "In progress",
            "content": "Happy driving!",
            "color": "rgb(0,204,0)"
        },
    },
    Booking.FLAKE: {
        'visible': True,
        'cancelable': True,
        'checkoutable': False,
        'pickupable': False,
        'details': {
            "status": "Waiting for documents",
            "content": "Please upload your driver documents.",
            "color": "rgb(255,51,51)"
        },
    },
    Booking.TOO_SLOW: {
        'visible': False,
        'cancelable': False,
        'checkoutable': False,
        'pickupable': False,
    },
    Booking.OWNER_REJECTED: {
        'visible': False,
        'cancelable': False,
        'checkoutable': False,
        'pickupable': False,
    },
    Booking.DRIVER_REJECTED: {
        'visible': False,
        'cancelable': False,
        'checkoutable': False,
        'pickupable': False,
    },
    Booking.MISSED: {
        'visible': False,
        'cancelable': False,
        'checkoutable': False,
        'pickupable': False,
    },
    Booking.TEST_BOOKING: {
        'visible': False,
        'cancelable': False,
        'checkoutable': False,
        'pickupable': False,
    },
    Booking.CANCELED: {
        'visible': False,
        'cancelable': False,
        'checkoutable': False,
        'pickupable': False,
    },
}


def states():
    return [state for (state, string) in Booking.STATE]

def visible_states():
    return [s for s in states() if state[s]['visible']]

def cancelable_states():
    return [s for s in states() if state[s]['cancelable']]
