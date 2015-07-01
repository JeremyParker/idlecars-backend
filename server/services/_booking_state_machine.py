# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from crm.services import ops_emails, driver_emails, owner_emails

from server.models import Booking


# list of trigger events
CREATED = 1
ALL_DOCS_UPLOADED = 2
SOMEONE_ELSE_BOOKED = 3
REMINDER_DELAY_PASSED = 4
DOCUMENTS_APPROVED = 5


def update_non_existent(booking, event):
    if event == CREATED:
        booking.state = Booking.PENDING
        ops_emails.new_booking_email(booking)
    return booking


def update_pending(booking, event):
    if event == ALL_DOCS_UPLOADED:
        booking.state = Booking.COMPLETE
        # note: don't email ops here. The driver service takes care of that.
    elif event == REMINDER_DELAY_PASSED:
        driver_emails.documents_reminder(booking)
        booking.state = server_models.Booking.FLAKE
    elif event == SOMEONE_ELSE_BOOKED:
        driver_email.someone_else_booked(booking)
        booking.state = server_models.Booking.TOO_SLOW
    return booking


def update_complete(booking, event):
    if event == DOCUMENTS_APPROVED:
        owner_emails.new_booking_email(booking)
        driver_emails.docs_approved_email(booking)
        booking.state = Booking.REQUESTED
    return booking


def update_flake(booking, event):
    if event == ALL_DOCS_UPLOADED:
        booking.state = Booking.COMPLETE
        # note: don't email ops here. The driver service takes care of that.
    elif event == SOMEONE_ELSE_BOOKED:
        driver_email.someone_else_booked(booking)
        booking.state = server_models.Booking.TOO_SLOW
    return booking


def do_nothing(booking, event):
    return booking


update_functions = {
    0: update_non_existent,
    Booking.PENDING: update_pending,
    Booking.COMPLETE: update_complete,
    Booking.REQUESTED: do_nothing,
    Booking.ACCEPTED: do_nothing,
    Booking.BOOKED: do_nothing,
    Booking.FLAKE: update_flake,
    Booking.TOO_SLOW: do_nothing,
    Booking.OWNER_REJECTED: do_nothing,
    Booking.DRIVER_REJECTED: do_nothing,
    Booking.MISSED : do_nothing,
    Booking.TEST_BOOKING : do_nothing,
    Booking.CANCELED : do_nothing,
}


def update(booking, event):
    origininal_state = booking.state
    booking = update_functions[origininal_state](booking)
    if booking.state == origininal_state:
        return booking
    else:
        return update(booking)
