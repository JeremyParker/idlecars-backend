# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from . import Booking


states = {
    Booking.PENDING: {
        'visible': True,
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
    },
    Booking.OWNER_REJECTED: {
        'visible': False,
    },
    Booking.DRIVER_REJECTED: {
        'visible': False,
    },
    Booking.MISSED: {
        'visible': False,
    },
    Booking.TEST_BOOKING: {
        'visible': False,
    },
    Booking.CANCELED: {
        'visible': False,
    },
}
