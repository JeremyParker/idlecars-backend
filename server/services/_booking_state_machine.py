# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from crm.services import ops_emails, driver_emails, owner_emails

from server.models import Booking


def pending_actions(booking):
    ops_emails.new_booking_email(booking)


def complete_actions(booking):
    pass # note: don't email ops here. The driver service takes care of that.


def requested_actions(booking):
    owner_emails.new_booking_email(booking)
    driver_emails.documents_approved(booking)


def flake_actions(booking):
    driver_emails.documents_reminder(booking)


def too_slow_actions(booking):
    driver_email.someone_else_booked(booking)


state_actions = {
    Booking.PENDING: pending_actions,
    Booking.COMPLETE: complete_actions,
    Booking.REQUESTED: requested_actions,
    Booking.FLAKE: flake_actions,
    Booking.TOO_SLOW: too_slow_actions,
}


def set_state(booking, state):
    if state in state_actions:
        state_actions[state](booking)
    booking.state = state
    return booking


def on_created(booking):
    if booking.driver.documentation_approved:
        return set_state(booking, Booking.REQUESTED)
    elif booking.driver.all_docs_uploaded():
        return set_state(booking, Booking.COMPLETE)
    else:
        return set_state(booking, Booking.PENDING)


def on_delay_passed(booking):
    return set_state(booking, Booking.FLAKE)


def on_documents_uploaded(booking):
    return set_state(booking, Booking.COMPLETE)


def on_documents_approved(booking):
    return set_state(booking, Booking.REQUESTED)


def on_someone_else_booked(booking):
    return set_state(booking, Booking.TOO_SLOW)
