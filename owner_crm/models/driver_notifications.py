# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

# don't import the class or the test will find it and try to test it as a notification.
from django import template as django_template
from django.template.loader import render_to_string
from django.conf import settings

from idlecars import email, fields

from owner_crm.models import notification


class SignupConfirmation(notification.DriverNotification):
    def get_context(self, **kwargs):
        sms_body = 'Hi {}, welcome to Idlecars where we make renting rideshare cars safe and easy. \
See our selection here: {}'.format(
            kwargs['driver_first_name'],
            kwargs['car_listing_url'],
        )
        text = '''
            Thank you for joining Idlecars, where we make renting for rideshare easy, safe, and affordable. <br />
            Drivers love us because we have their back. We fight to make sure drivers never get stuck with
            bad rental terms, and never pay too much for a rental. We source cars from owners across NYC,
            which means that you get the best price. And with our online rental process we cut down the time
            it takes for you to get into a car. <br />
            Click below to start renting.
        '''

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Welcome to Idlecars!',
            'TEXT': text,
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'subject': 'Welcome to Idlecars',
            'template_name': 'one_button_no_image',
            'sms_body': sms_body,
        }


class SignupFirstReminder(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = render_to_string(
            "signup_reminder.jade",
            {},
            django_template.Context(autoescape=False)
        )
        sms_body = 'Hi {}, it\'s Idlecars! Come experience a better way to rent for \
rideshare: {}'.format(
            kwargs['driver_first_name'],
            kwargs['car_listing_url'],
        )

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'How to rent a car with Idlecars',
            'TEXT': text,
            'CTA_LABEL': 'Find a car here',
            'CTA_URL': kwargs['car_listing_url'],
            'subject': 'How Idlecars works',
            'template_name': 'one_button_no_image',
            'sms_body': sms_body,
        }


class SignupSecondReminder(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = render_to_string(
            "signup_reminder.jade",
            {},
            django_template.Context(autoescape=False)
        )
        sms_body = 'Hi {}, it\'s Idlecars. Are you still interested in renting? \
Visit us at {} or let us know what you are looking for!'.format(
            kwargs['driver_first_name'],
            kwargs['car_listing_url'],
        )

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Find a car for Uber, Lyft or Via',
            'TEXT': text,
            'CTA_LABEL': 'Find a car here',
            'CTA_URL': kwargs['car_listing_url'],
            'subject': 'Do you need a car for Uber, Lyft, or Via?',
            'template_name': 'one_button_no_image',
            'sms_body': sms_body,
        }


class SignupCredit(notification.DriverNotification):
    def get_context(self, **kwargs):
        subject = 'You have ${} towards an Idlecars rental'.format(kwargs['driver_credit'])
        cta_url = kwargs['car_listing_url']
        text = 'Thank you for entering your Idlecars referral code! \
You have ${} towards your next rental.'.format(kwargs['driver_credit'])

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': subject,
            'TEXT': text,
            'CTA_LABEL': 'Find a car here',
            'CTA_URL': cta_url,
            'subject': subject,
            'template_name': 'one_button_no_image',
            'sms_body': text + ' Find a car here: ' + cta_url
        }


class ReferFriends(notification.DriverNotification):
    def custom_params_sets(self):
        return ['credit']

    def get_context(self, **kwargs):
        sms_body = 'Do you love Idlecars? Receive ${} of Idlecars rental credit when \
you refer your friends with this code: {}.'.format(
            kwargs['credit_amount_invitor'],
            kwargs['credit_code'],
        )

        subject = 'Receive ${} for each friend you refer to Idlecars'.format(
            kwargs['credit_amount_invitor'],
        )

        text = '''
            Thank you for renting with Idlecars! <br />
            Now that you are on the road, you have the chance to save on your weekly rent.
            Every time you refer another driver with the code below they will get ${} towards
            their first rental and you will get ${} for each driver you refer -
            that money will go towards your weekly rent! <br /> <br />
            Your Code: {} <br /> <br />
            How it works:
            <ul><li> Send the code to your friend </li>
            <li> They rent a car with Idlecars </li>
            <li> We give you ${} to be used for your next payment </li> </ul>
        '''.format(
            kwargs['credit_amount_invitee'],
            kwargs['credit_amount_invitor'],
            kwargs['credit_code'],
            kwargs['credit_amount_invitor'],
        )

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': subject,
            'TEXT': text,
            'template_name': 'no_button_no_image',
            'subject': subject,
            'sms_body': sms_body,
        }


class DocsApprovedNoBooking(notification.DriverNotification):
    def get_context(self, **kwargs):
        subject = 'Welcome to idlecars, {driver_full_name}!'.format(**kwargs)
        headline = 'Your documents have been received.'
        text = 'You are now ready to rent any car on idlecars with one tap!'
        cta_url = kwargs['car_listing_url']

        return {
            'FNAME': kwargs['driver_email'],
            'HEADLINE': headline,
            'TEXT': text,
            'CTA_LABEL': 'Rent a car now',
            'CTA_URL': cta_url,
            'subject': subject,
            'template_name': 'one_button_no_image',
            'sms_body': subject + ' ' + headline + ' ' + text + ' Tap here to rent a car now: ' + cta_url
        }


def _render_booking_reminder_body(body_template, car_name, missing_docs_html):
    template_data = {
        'CAR_NAME': car_name,
        'DOCS_LIST': missing_docs_html,
    }
    return render_to_string(body_template, template_data, django_template.Context(autoescape=False))


def _render_driver_reminder_body(body_template, missing_docs_html):
    template_data = {
        'DOCS_LIST': missing_docs_html,
    }
    return render_to_string(body_template, template_data, django_template.Context(autoescape=False))


class FirstDocumentsReminderBooking(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': _render_booking_reminder_body(
                'first_docs_reminder_booking.jade',
                kwargs['car_name'],
                kwargs['missing_docs_html'],
            ),
            'CTA_LABEL': 'Upload Documents Now',
            'CTA_URL': kwargs['docs_upload_url'],
            'HEADLINE': 'Your {} is waiting'.format(kwargs['car_name']),
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Your {} is waiting on your driver documents'.format(kwargs['car_name']),
            'sms_body': 'We noticed that you tried to book a {}, but haven\'t finished \
submitting your documents for the insurance. To start driving, you still need to submit these documents: \n{} \
Tap here to upload them: \
{}'.format(kwargs['car_name'], kwargs['missing_docs_list'], kwargs['docs_upload_url'])
        }


class FirstDocumentsReminderDriver(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': _render_driver_reminder_body(
                'first_docs_reminder_driver.jade',
                kwargs['missing_docs_html'],
            ),
            'CTA_LABEL': 'Upload Documents Now',
            'CTA_URL': kwargs['docs_upload_url'],
            'HEADLINE': 'Don\'t forget to upload your documents for idlecars',
            'template_name': 'one_button_no_image',
            'subject': 'Submit your documents now so you are ready to drive later.',
            'sms_body': 'Don\'t forget to upload your documents for idlecars. \
You’ve successfully created an account, now you can upload your missing documents so it\'s easier to rent whenever you want: {}. \
Tap here to upload now: {}'.format(kwargs['missing_docs_list'], kwargs['docs_upload_url']),
        }


class SecondDocumentsReminderBooking(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': _render_booking_reminder_body(
                'second_docs_reminder_booking.jade',
                kwargs['car_name'],
                kwargs['missing_docs_html'],
            ),
            'CTA_LABEL': 'Upload Documents Now',
            'CTA_URL': kwargs['docs_upload_url'],
            'HEADLINE': 'Your {} is waiting'.format(kwargs['car_name']),
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Your {} is still waiting on your driver documents'.format(kwargs['car_name']),
            'sms_body': 'We noticed that you tried to book a {}, but haven\'t finished \
submitting your documents for the insurance. To start driving, you still need to submit these documents: \n{} \
Tap here to upload them: \
{}'.format(kwargs['car_name'], kwargs['missing_docs_list'], kwargs['docs_upload_url'])
        }


class SecondDocumentsReminderDriver(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': _render_driver_reminder_body(
                'second_docs_reminder_driver.jade',
                kwargs['missing_docs_html'],
            ),
            'CTA_LABEL': 'Upload Documents Now',
            'CTA_URL': kwargs['docs_upload_url'],
            'HEADLINE': 'Don\'t forget to upload your documents for idlecars',
            'template_name': 'one_button_no_image',
            'subject': 'Are you ready to drive?',
            'sms_body': 'Don\'t forget to upload your documents for idlecars. \
You’ve successfully created an account, now you can upload your missing documents so it\'s easier to rent whenever you want: {}. \
Tap here to upload now: {}'.format(kwargs['missing_docs_list'], kwargs['docs_upload_url']),
        }


class ThirdDocumentsReminderBooking(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': _render_booking_reminder_body(
                'third_docs_reminder_booking.jade',
                kwargs['car_name'],
                kwargs['missing_docs_html'],
            ),
            'CTA_LABEL': 'Upload Documents Now',
            'CTA_URL': kwargs['docs_upload_url'],
            'HEADLINE': 'Your {} is waiting'.format(kwargs['car_name']),
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Don’t miss your rental, submit your driver documents',
            'sms_body': 'We noticed that you tried to book a {}, but haven\'t finished \
submitting your documents for the insurance. To start driving, you still need to submit these documents: \n{} \
Tap here to upload them: \
{}'.format(kwargs['car_name'], kwargs['missing_docs_list'], kwargs['docs_upload_url'])
        }


class ThirdDocumentsReminderDriver(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': _render_driver_reminder_body(
                'second_docs_reminder_driver.jade',
                kwargs['missing_docs_html'],
            ),
            'CTA_LABEL': 'Upload Documents Now',
            'CTA_URL': kwargs['docs_upload_url'],
            'HEADLINE': 'Don\'t forget to upload your documents for idlecars',
            'template_name': 'one_button_no_image',
            'subject': 'Are you ready to drive?',
            'sms_body': 'Don\'t forget to upload your documents for idlecars. \
You’ve successfully created an account, now you can upload your missing documents so it\'s easier to rent whenever you want: {}. \
Tap here to upload now: {}'.format(kwargs['missing_docs_list'], kwargs['docs_upload_url']),
        }


class BookingTimedOut(notification.DriverNotification):
    def get_context(self, **kwargs):
        if kwargs['driver_all_docs_uploaded']:
            template = 'booking_timed_out_cc.jade'
            subject = 'Your {} rental has been cancelled because you never checked out.'.format(
                kwargs['car_name']
            )
        else:
            template = 'booking_timed_out.jade'
            subject = 'Your rental has been cancelled because we don\'t have your driver documents.'

        template_data = {
            'CAR_NAME': kwargs['car_name'],
        }

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': render_to_string(template, template_data, django_template.Context(autoescape=False)),
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'HEADLINE': 'Your {} rental was canceled'.format(kwargs['car_name']),
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': subject,
            'sms_body': 'We\’re sorry. ' + subject + ' But don’t worry! You can always come back and find another car! \
Tap here to find another car today: {}'.format(kwargs['car_listing_url']),
        }


class AwaitingInsuranceEmail(notification.DriverNotification):
    def get_context(self, **kwargs):
        template_data = {
            'CAR_NAME': kwargs['car_name']
        }
        body = render_to_string("driver_docs_approved.jade", template_data, django_template.Context(autoescape=False))

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': body,
            'CTA_LABEL': 'See your rental',
            'CTA_URL': kwargs['bookings_url'],
            'HEADLINE': 'Your documents have been submitted for insurance approval',
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Congratulations! Your documents have been submitted!',
            'sms_body': 'Hi {}, Your documents have been \
submitted to the owner for final insurance approval of the {} you reserved! You \
should be ready to drive within 24-48 hours! Hang tight!'.format(kwargs['driver_first_name'], kwargs['car_name'])
        }


class FirstInsuranceNotification(notification.DriverNotification):
    def get_context(self, **kwargs):
        subject = 'We are still working to get you on the {}’s insurance.'.format(kwargs['car_name'])
        sms_body = 'Hi {}, we are still working to get you on the {}’s insurance. We will \
let you know as soon as the car is ready for pickup.'.format(
            kwargs['driver_first_name'] or None,
            kwargs['car_name'],
        )
        text = '''We are still working to get you on the {}’s insurance. We will let you know
        as soon as the car is ready for pickup.'''.format(
            kwargs['car_name'],
        )

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': text,
            'HEADLINE': subject,
            'template_name': 'no_button_no_image',
            'subject': subject,
            'sms_body': sms_body,
        }


class SecondInsuranceNotification(notification.DriverNotification):
    def get_context(self, **kwargs):
        subject = 'We told the owner to get you on the insurance ASAP'
        sms_body = 'Hi {}, we told the owner of the {} to get you on the insurance ASAP, \
so you shouldn’t have to wait much longer!'.format(
            kwargs['driver_first_name'] or None,
            kwargs['car_name'],
        )
        text = 'We told the owner of the {} to get you on the insurance ASAP, so you shouldn’t \
        have to wait much longer!'.format(
            kwargs['car_name'],
        )
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': text,
            'HEADLINE': subject,
            'template_name': 'no_button_no_image',
            'subject': subject,
            'sms_body': sms_body,
        }


def base_letter_rejected(driver):
    if not driver.email():
        return
    #TODO: send something to driver


class InsuranceApproved(notification.DriverNotification):
    def get_context(self, **kwargs):
        template_data = {
            'CAR_NAME': kwargs['car_name'],
        }
        body = render_to_string("driver_insurance_approved.jade", template_data, django_template.Context(autoescape=False))

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'You have been added to your car\'s insurance',
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'TEXT': body,
            'CTA_LABEL': 'Pick up your car',
            'CTA_URL': kwargs['bookings_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Alright! Your {} is ready to pick up!'.format(kwargs['car_name']),
            'sms_body': 'Congratulations! You have been approved to drive the {}!\
How to pick up your car:\n\
Tap here to go to My Rentals in the idlecars app: {}\n\
Tap "Arrange to pick up your car".\n\
Call the owner to schedule meet and pick up the car.\n\
When you meet the owner, inspect the car and make sure it meets your expectations.\n\
Follow the instructions in the app and click “Pay & Drive” to pay the first week\'s rent.\n\
The owner will receive a notification, and give you the keys.\n\
Need help? Contact us:\n\
1-844-IDLECAR (1-844-435-3227)'.format(kwargs['car_name'], kwargs['bookings_url'])
        }


class InsuranceRejected(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = 'We didn\'t manage to get you on the insurance for the car you wanted. But now that your \
account is complete, you can pick another car, and we\'ll add you to the insurance on that one. '

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Sorry, we couldn\'t get you on the insurance.',
            'TEXT': text,
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'You couldn\'t be added to the insurance on the car you wanted',
            'sms_body': 'Sorry {}, '.format(kwargs['driver_first_name']) + text + kwargs['car_listing_url']
        }


class InsuranceFailed(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = 'We\'re sorry, but we were unable to get you in your {} due to an issue with \
the owner. Your deposit has been fully refunded. We sincerely apologize for any inconvenience. \
Now that your account is complete, you can pick another car and we\'ll start processing your \
new rental immediately. '.format(kwargs['car_name'])
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Sorry, We were unable to complete your rental.',
            'TEXT': text,
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'We were unable to complete your {} booking'.format(kwargs['car_name']),
            'sms_body': text + kwargs['car_listing_url']
        }


class CarRentedElsewhere(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = 'Sorry, someone else has rented the car you wanted. Sometimes that happens. Still, \
there are plenty more great cars available. '
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Sorry, the car you wanted was rented out by someone else.',
            'TEXT': '''{}
            <br />
            <p>Need help? Contact us:</p>
            <p>support@idlecars.com </p>
            <p>'''.format(text) + settings.IDLECARS_PHONE_NUMBER + '</p>',
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Sorry, someone else rented out the car you wanted.',
            'sms_body': text + kwargs['car_listing_url']
        }


class CheckoutReceipt(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = '''We put a hold of ${} on your credit card. You will not be charged until \
you inspect and approve the car in the app. When you pick up the car, the deposit will be \
processed, and your card will be charged for the first week's rent. Your documents have \
been submitted to the owner for insurance approval. You will be notified in 24-48 hours when \
you are approved. If you have questions please contact {} at {}.'''.format(
                kwargs['car_deposit'],
                kwargs['owner_name'],
                fields.format_phone_number(kwargs['owner_phone_number']),
            )
        subject = 'Your {} was successfully reserved.'.format(kwargs['car_name'])
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Your {} was successfully reserved'.format(kwargs['car_name']),
            'TEXT': text,
            'template_name': 'no_button_no_image',
            'subject': subject,
            'sms_body': subject + ' ' + text
        }


class InvitorReceivedCredit(notification.DriverNotification):
    def custom_params_sets(self):
        return ['credit']

    def get_context(self, **kwargs):
        text = '''
            You just received ${} of rental credit because someone rented a car with
            Idlecars and used your code! You now have ${} of Idlecars credit to use
            towards your next Idlecars rental. <br />
            If you are already driving, this amount will be taken off your next rental payment. <br />
            If you haven’t rented with us yet, you can use this credit towards your next rental! <br />
            <br />
            Click below to see our current selection of cars
        '''.format(kwargs['credit_amount_invitor'], kwargs['driver_credit'])
        subject = 'You just received ${} of Idlecars rental credit'.format(kwargs['credit_amount_invitor'])
        sms_body = 'Hi {}, someone signed up using your Idlecars referral code! \
You just received ${} towards your next rental!'.format(
            kwargs['driver_first_name'],
            kwargs['credit_amount_invitor'],
        )
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': subject,
            'TEXT': text,
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': subject,
            'sms_body': sms_body,
        }


class FirstPickupReminder(notification.DriverNotification):
    def get_context(self, **kwargs):
        sms_body = 'Have you scheduled the pickup for the {}? Make sure when you pick it up you \
go to your booking page click the blue “Pay and Drive” button.'.format(kwargs['car_name'])
        text ='''Please open the Idlecars app to find the owner's phone number to coordinate pickup.
        When you pick up the car make sure you go back to the booking page (link below) and click
        the blue “Pay and Drive” button to make your first week’s payment – DO NOT PAY CASH!
        <br /><br />
        You should go pickup the car and then you can register for the rideshare company of your
         choice. You must have these documents with you:
        <ul><li> The insurance document (emailed from Idlecars) </li>
        <li> The FH1 - NY State insurance (receive from owner at pickup) </li>
        <li> The registration document (receive from owner at pickup) </li></ul>'''

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Remember to schedule your pickup',
            'TEXT': text,
            'CTA_LABEL': 'Your rental',
            'CTA_URL': kwargs['bookings_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Have you scheduled a time to pickup your {}'.format(kwargs['car_name']),
            'sms_body': sms_body,
        }


class SecondPickupReminder(notification.DriverNotification):
    def get_context(self, **kwargs):
        sms_body = 'Have you scheduled the pickup for the {}? Make sure when you pick it up you \
go to your booking page click the blue “Pay and Drive” button.'.format(kwargs['car_name'])
        text ='''If you haven’t already, please open the Idlecars app to find the owner's phone
        number to coordinate pickup. <br />
        When you pick up the car make sure you go back to the booking page (link below) and click
        the blue “Pay and Drive” button to make your first week’s payment – DO NOT PAY CASH!

        <br /><br />
        You should go pickup the car and then you can register for the rideshare company of your
         choice. You must have these documents with you:
        <ul><li> The insurance document (emailed from Idlecars) </li>
        <li> The FH1 - NY State insurance (receive from owner at pickup) </li>
        <li> The registration document (receive from owner at pickup) </li></ul>'''

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Remember to click the blue “Pay and Drive” button at pickup',
            'TEXT': text,
            'CTA_LABEL': 'Your rental',
            'CTA_URL': kwargs['bookings_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Your {} rental – how to pay and drive'.format(kwargs['car_name']),
            'sms_body': sms_body,
        }


class PickupConfirmation(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = 'Success! Your card has been charged {} for the {} booking. \
You have used ${} of Idlecars credit. \
The owner will receive a notification that the payment was processed and should \
give you the keys to start driving. Please contact us if there are any issues.'.format(
                kwargs['payment_cash_amount'],
                kwargs['car_name'],
                kwargs['payment_credit_amount'],
            )
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'You are ready to drive!',
            'TEXT': text,
            'template_name': 'no_button_no_image',
            'subject': 'You are ready to drive!',
            'sms_body': text,
        }


class PaymentReceipt(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = '''
            Your weekly rental fee has been paid. <br />
            Driver: {} <br />
            Car: {} <br /><br />

            Invoice Period: {} - {} <br />
            Rental Amount: ${} <br />
        '''
        if kwargs['payment_credit_amount'] > 0:
            text += '''
                Driver Credit: ${} <br />
                Payment Amount: ${} <br />
            '''.format(
                kwargs['payment_credit_amount'],
                kwargs['payment_cash_amount'],
            )

        if kwargs['booking_next_payment_amount'] > 0:
            text += 'Your next payment of ${} will occur on {} <br />'.format(
                kwargs['booking_next_payment_amount'],
                kwargs['booking_invoice_end_time'].strftime('%b %d'),
            )
        else:
            text += 'This is your last payment. <br />'

        text += 'Your rental will end on {}. <br /><br />Thank you for using idlecars.'
        text = text.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
            kwargs['payment_invoice_start_time'].strftime('%b %d'),
            kwargs['payment_invoice_end_time'].strftime('%b %d'),
            kwargs ['payment_total_amount'],
            kwargs['booking_end_time'].strftime('%b %d'),
        )

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Payment Received: {} Booking'.format(kwargs['car_name']),
            'TEXT': text,
            'template_name': 'no_button_no_image',
            'subject': 'Payment Received: {} Booking'.format(kwargs['car_name']),
        }


class PaymentFailed(notification.DriverNotification):
    def get_context(self, **kwargs):
        sms_body = 'Hi {}, your payment for the {} failed. We will try to charge your card again in \
8 hours. Please make sure you have the funds available.'.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
        )
        text = '''Your payment for the {} failed. We will try to charge your card again in 8 hours.
        Please make sure you have the funds available.'''.format(kwargs['car_name'])

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Your {} rental payment had failed.'.format(kwargs['car_name']),
            'TEXT': text,
            'template_name': 'no_button_no_image',
            'subject': 'Your {} rental payment had failed.'.format(kwargs['car_name']),
            'sms_body': sms_body,
        }


class SomeoneElseBooked(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = 'While we were waiting for you to finish uploading your documents, \
another driver rented your {}. But don\'t worry, there are plenty more cars \
available. '.format(kwargs['car_name'])
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Someone else rented your car!',
            'TEXT': text,
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Someone else rented your {}.'.format(kwargs['car_name']),
            'sms_body': text + kwargs['car_listing_url']
        }


class BookingCanceled(notification.DriverNotification):
    def get_context(self, **kwargs):
        body = '''
            Your {} rental has been canceled. Now you can go back to idlecars and rent another car!
        '''.format(kwargs['car_name'])

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': body,
            'CTA_LABEL': 'Find another car',
            'CTA_URL': kwargs['car_listing_url'],
            'HEADLINE': 'Your rental has been canceled',
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Confirmation: Your rental has been canceled.',
            'sms_body': body + ' Tap here: {}'.format(kwargs['car_listing_url']),
        }


class ExtendReminder(notification.DriverNotification):
    def get_context(self, **kwargs):
        sms_body = 'Hi {}, Your {} rental is due back in 24 hours. Either notify the owner that you \
will return it, or go to your booking page and click “Change End Date” to extend your rental.'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
        )
        text = '''Your rental ends in 24 hours, so you either have to schedule a drop-off or extend
        the duration of your rental. <br /><br />

        How to extend your rental:
        <ul><li> Go to your booking page </li>
        <li> Click “Change End Date” </li>
        <li> Choose a new end date for your rental </li></ul>
        <br />
        How to drop off your car:
        <ul><li>  Call the owner to schedule the drop-off </li>
        <li> Drop off the car on that specific time and date </li></ul>'''

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Your rental ends in 24 hours',
            'TEXT': text,
            'CTA_LABEL': 'My rental',
            'CTA_URL': kwargs['bookings_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Your rental ends in 24 hours',
            'sms_body': sms_body,
        }


class FirstLateNotice(notification.DriverNotification):
    def get_context(self, **kwargs):
        sms_body = 'Hi {}, Your {} rental was due back 12 hours ago. Please contact the owner and \
let them know when you will return the car or we will have to report the car stolen to the local \
authorities'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
        )
        text = '''Your rental ended 12 hours ago hours ago. Please contact the owner and let them
        know when you will return the car or we will have to report the car stolen to the local
        authorities.'''

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Your rental ended 12 hours ago',
            'TEXT': text,
            'template_name': 'no_button_no_image',
            'subject': 'Your rental ended 12 hours ago',
            'sms_body': sms_body,
        }


class SecondLateNotice(notification.DriverNotification):
    def get_context(self, **kwargs):
        sms_body = 'Hi {}, Your {} rental was due back 24 hours ago. If you do not return the car \
soon we will have to report the car stolen to the local authorities.'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
        )
        text = '''Your rental ended 12 hours ago hours ago. Please contact the owner and let them
        know when you will return the car or we will have to report the car stolen to the local
        authorities.'''

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Your rental ended 24 hours ago',
            'TEXT': text,
            'template_name': 'no_button_no_image',
            'subject': 'Please return your {}'.format(kwargs['car_name']),
            'sms_body': sms_body,
        }


class DepositRefunded(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = '''Nice! the owner confirmed that the {} has been returned, IdleCars is looking
        forward to serve you next time!'''.format(
            kwargs['car_name'],
            kwargs['payment_cash_amount'],
        )

        if kwargs['payment_cash_amount']:
            text += 'Also, your deposit ${} has been refunded'.format(kwargs['payment_cash_amount'])

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Your return has been cofirmed.',
            'TEXT': text,
            'template_name': 'no_button_no_image',
            'subject': 'Your return has been confirmed.',
            'sms_body': text,
        }


class PasswordReset(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = 'We\'ve received a request to reset your password. If you didn\'t make the request, just \
ignore this message. Otherwise, you can reset your password using this link: '
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'HEADLINE': 'Reset your password',
            'TEXT': text,
            'CTA_LABEL': 'Reset password',
            'CTA_URL': kwargs['driver_password_reset_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Reset your idlecars password.',
            'sms_body': text + kwargs['driver_password_reset_url'],
        }


class PasswordResetConfirmation(notification.DriverNotification):
    def get_context(self, **kwargs):
        subject = 'Your idlecars password has been set.'
        text = 'If you didn\'t set your password, or if you think something funny is going \
on, please call us any time at ' + settings.IDLECARS_PHONE_NUMBER + '.'
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'HEADLINE': 'Your account password has been set',
            'TEXT': text,
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': subject,
            'sms_body': subject + ' ' + text,
        }


class UseYourCredit(notification.DriverNotification):
    def get_context(self, **kwargs):
        subject = 'You have ${} to use towards your next rental'.format(kwargs['driver_credit'])
        text = 'Don’t forget! You have ${} for your next rental. See our current car selection \
here <br /> Click below to see our current selection! <br />'.format(kwargs['driver_credit'])
        sms_body = 'Hi {} don’t forget that you have ${} for your next rental. \
 See our current car selection here: {}'.format(
                kwargs['driver_first_name'],
                kwargs['driver_credit'],
                kwargs['car_listing_url'],
            )

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': subject,
            'TEXT': text,
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': subject,
            'sms_body': sms_body,
        }


class InactiveCredit(notification.DriverNotification):
    def __init__(self, campaign_name, argument, *args):
        super(InactiveCredit, self).__init__(campaign_name, argument)
        self.credit = args[0]

    def get_context(self, **kwargs):
        text = '''
            We haven’t seen you in a while! We’d like to help you out! <br />

            We have gone ahead and applied a ${} credit to your account to be used towards your next rental.
            To claim your cash, all you need to do is click the link below and complete a rental with Idlecars
            and the money will be automatically deducted from your first week's rent. <br />

            Click below to find a car.
        '''.format(self.credit)
        sms_body = 'Hi {}, we have given you ${} to use on your next rental! Click here to book a car and claim your cash. \
Find a car here: {}'.format(
            kwargs['driver_first_name'],
            self.credit,
            kwargs['car_listing_url'],
        )

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Collect some Idle Cash',
            'TEXT': text,
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Let us give you cash towards your rental',
            'sms_body': sms_body,
        }


class InactiveReferral(notification.DriverNotification):
    def custom_params_sets(self):
        return ['credit']

    def get_context(self, **kwargs):
        sms_body = 'Give your friends ${} of Idlecars credit  with code {} and get ${} for \
every friend that rents a car with Idlecars: {}'.format(
            kwargs['credit_amount_invitee'],
            kwargs['credit_code'],
            kwargs['credit_amount_invitor'],
            kwargs['car_listing_url'],
        )
        text = '''
            Need some extra money to help with your rental? Want to share some saving with your friends?  <br />
            Now that you have an Idlecars account, you have the chance to save on your weekly rent.
            Every time you refer another driver with the code below they will get ${} towards their
            first rental and you will get ${} for each driver you refer -
            that money will go towards your weekly rent! <br /> <br />
            Your Code: {} <br /><br />
            How it works:
            <ul><li> Send the code to your friend
                <li> They rent a car with Idlecars </li>
                <li> We give you ${} to be used for your next payment </li></ul>
            <br />
            Don’t have a car yet? Click below to find one!
        '''.format(
            kwargs['credit_amount_invitee'],
            kwargs['credit_amount_invitor'],
            kwargs['credit_code'],
            kwargs['credit_amount_invitor'],
        )
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': ' Share some Idle Cash with your friends and save on your next rental',
            'TEXT': text,
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Share some Idle Cash with your friends and save on your next rental',
            'sms_body': sms_body,
        }
