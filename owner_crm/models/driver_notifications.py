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
        sms_body = 'Hi {}, Welcome to All Taxi. \
See our selection of cars here: {}'.format(
            kwargs['driver_first_name'],
            kwargs['car_listing_url'],
        )
        text = '''
            Thank you for signing up at All Taxi. <br />
            Click below to find a car you'd like to be added to.
        '''

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Welcome to All Taxi!',
            'TEXT': text,
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'subject': 'Welcome to All Taxi',
            'template_name': 'one_button_no_image',
        }


# class SignupFirstReminder(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         text = render_to_string(
#             "signup_reminder.jade",
#             {},
#             django_template.Context(autoescape=False)
#         )
#         sms_body = 'Hi {}, it\'s Idlecars! Come experience a better way to rent for \
# rideshare: {}'.format(
#             kwargs['driver_first_name'],
#             kwargs['car_listing_url'],
#         )

#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': 'How to rent a car with Idlecars',
#             'TEXT': text,
#             'CTA_LABEL': 'Find a car here',
#             'CTA_URL': kwargs['car_listing_url'],
#             'subject': 'How All Taxi works',
#             'template_name': 'one_button_no_image',
#             'sms_body': sms_body,
#         }


# class SignupSecondReminder(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         text = render_to_string(
#             "signup_reminder.jade",
#             {},
#             django_template.Context(autoescape=False)
#         )
#         sms_body = 'Hi {}, it\'s Idlecars. Are you still interested in renting? \
# Visit us at {} or let us know what you are looking for!'.format(
#             kwargs['driver_first_name'],
#             kwargs['car_listing_url'],
#         )

#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': 'Find a car for Uber, Lyft or Via',
#             'TEXT': text,
#             'CTA_LABEL': 'Find a car here',
#             'CTA_URL': kwargs['car_listing_url'],
#             'subject': 'Do you need a car for Uber, Lyft, or Via?',
#             'template_name': 'one_button_no_image',
#             'sms_body': sms_body,
#         }


# class SignupCredit(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         subject = 'You have ${} towards an Idlecars rental'.format(kwargs['driver_credit'])
#         cta_url = kwargs['car_listing_url']
#         text = 'Thank you for entering your Idlecars referral code! \
# You have ${} towards your next rental.'.format(kwargs['driver_credit'])

#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': subject,
#             'TEXT': text,
#             'CTA_LABEL': 'Find a car here',
#             'CTA_URL': cta_url,
#             'subject': subject,
#             'template_name': 'one_button_no_image',
#             'sms_body': text + ' Find a car here: ' + cta_url
#         }


# class ReferFriends(notification.DriverNotification):
#     def custom_params_sets(self):
#         return ['credit']

#     def get_context(self, **kwargs):
#         sms_body = 'Do you love Idlecars? Receive ${} of Idlecars rental credit when \
# you refer your friends with this code: {}.'.format(
#             kwargs['credit_amount_invitor'],
#             kwargs['credit_code'],
#         )

#         subject = 'Receive ${} for each friend you refer to Idlecars'.format(
#             kwargs['credit_amount_invitor'],
#         )

#         text = '''
#             Thank you for renting with Idlecars! <br />
#             Now that you are on the road, you have the chance to save on your weekly rent.
#             Every time you refer another driver with the code below they will get ${} towards
#             their first rental and you will get ${} for each driver you refer -
#             that money will go towards your weekly rent! <br /> <br />
#             Your Code: {} <br /> <br />
#             How it works:
#             <ul><li> Send the code to your friend </li>
#             <li> They rent a car with Idlecars </li>
#             <li> We give you ${} to be used for your next payment </li> </ul>
#         '''.format(
#             kwargs['credit_amount_invitee'],
#             kwargs['credit_amount_invitor'],
#             kwargs['credit_code'],
#             kwargs['credit_amount_invitor'],
#         )

#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': subject,
#             'TEXT': text,
#             'template_name': 'no_button_no_image',
#             'subject': subject,
#             'sms_body': sms_body,
#         }


class DocsApprovedNoBooking(notification.DriverNotification):
    def get_context(self, **kwargs):
        subject = 'Welcome to All Taxi, {driver_full_name}!'.format(**kwargs)
        headline = 'Your documents have been received.'
        text = 'You are now ready to rent any car with one tap!'
        cta_url = kwargs['car_listing_url']

        return {
            'FNAME': 'driver_full_name'.format(**kwargs),
            'HEADLINE': headline,
            'TEXT': text,
            'CTA_LABEL': 'Find a car now',
            'CTA_URL': cta_url,
            'subject': subject,
            'template_name': 'one_button_no_image',
        }


# def _render_booking_reminder_body(body_template, car_name, missing_docs_html):
#     template_data = {
#         'CAR_NAME': car_name,
#         'DOCS_LIST': missing_docs_html,
#     }
#     return render_to_string(body_template, template_data, django_template.Context(autoescape=False))


# def _render_driver_reminder_body(body_template, missing_docs_html):
#     template_data = {
#         'DOCS_LIST': missing_docs_html,
#     }
#     return render_to_string(body_template, template_data, django_template.Context(autoescape=False))


# class FirstDocumentsReminderBooking(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'TEXT': _render_booking_reminder_body(
#                 'first_docs_reminder_booking.jade',
#                 kwargs['car_name'],
#                 kwargs['missing_docs_html'],
#             ),
#             'CTA_LABEL': 'Upload Documents Now',
#             'CTA_URL': kwargs['docs_upload_url'],
#             'HEADLINE': 'Your {} is waiting'.format(kwargs['car_name']),
#             'CAR_IMAGE_URL': kwargs['car_image_url'],
#             'template_name': 'one_button_one_image',
#             'subject': 'Your {} is waiting on your driver documents'.format(kwargs['car_name']),
#             'sms_body': 'We noticed that you tried to book a {}, but haven\'t finished \
# submitting your documents for the insurance. To start driving, you still need to submit these documents: \n{} \
# Tap here to upload them: \
# {}'.format(kwargs['car_name'], kwargs['missing_docs_list'], kwargs['docs_upload_url'])
#         }


# class FirstDocumentsReminderDriver(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'TEXT': _render_driver_reminder_body(
#                 'first_docs_reminder_driver.jade',
#                 kwargs['missing_docs_html'],
#             ),
#             'CTA_LABEL': 'Upload Documents Now',
#             'CTA_URL': kwargs['docs_upload_url'],
#             'HEADLINE': 'Don\'t forget to upload your documents for idlecars',
#             'template_name': 'one_button_no_image',
#             'subject': 'Submit your documents now so you are ready to drive later.',
#             'sms_body': 'Don\'t forget to upload your documents for idlecars. \
# You’ve successfully created an account, now you can upload your missing documents so it\'s easier to rent whenever you want: {}. \
# Tap here to upload now: {}'.format(kwargs['missing_docs_list'], kwargs['docs_upload_url']),
#         }


# class SecondDocumentsReminderBooking(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'TEXT': _render_booking_reminder_body(
#                 'second_docs_reminder_booking.jade',
#                 kwargs['car_name'],
#                 kwargs['missing_docs_html'],
#             ),
#             'CTA_LABEL': 'Upload Documents Now',
#             'CTA_URL': kwargs['docs_upload_url'],
#             'HEADLINE': 'Your {} is waiting'.format(kwargs['car_name']),
#             'CAR_IMAGE_URL': kwargs['car_image_url'],
#             'template_name': 'one_button_one_image',
#             'subject': 'Your {} is still waiting on your driver documents'.format(kwargs['car_name']),
#             'sms_body': 'We noticed that you tried to book a {}, but haven\'t finished \
# submitting your documents for the insurance. To start driving, you still need to submit these documents: \n{} \
# Tap here to upload them: \
# {}'.format(kwargs['car_name'], kwargs['missing_docs_list'], kwargs['docs_upload_url'])
#         }


# class SecondDocumentsReminderDriver(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'TEXT': _render_driver_reminder_body(
#                 'second_docs_reminder_driver.jade',
#                 kwargs['missing_docs_html'],
#             ),
#             'CTA_LABEL': 'Upload Documents Now',
#             'CTA_URL': kwargs['docs_upload_url'],
#             'HEADLINE': 'Don\'t forget to upload your documents for idlecars',
#             'template_name': 'one_button_no_image',
#             'subject': 'Are you ready to drive?',
#             'sms_body': 'Don\'t forget to upload your documents for idlecars. \
# You’ve successfully created an account, now you can upload your missing documents so it\'s easier to rent whenever you want: {}. \
# Tap here to upload now: {}'.format(kwargs['missing_docs_list'], kwargs['docs_upload_url']),
#         }


# class ThirdDocumentsReminderBooking(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'TEXT': _render_booking_reminder_body(
#                 'third_docs_reminder_booking.jade',
#                 kwargs['car_name'],
#                 kwargs['missing_docs_html'],
#             ),
#             'CTA_LABEL': 'Upload Documents Now',
#             'CTA_URL': kwargs['docs_upload_url'],
#             'HEADLINE': 'Your {} is waiting'.format(kwargs['car_name']),
#             'CAR_IMAGE_URL': kwargs['car_image_url'],
#             'template_name': 'one_button_one_image',
#             'subject': 'Don’t miss your rental, submit your driver documents',
#             'sms_body': 'We noticed that you tried to book a {}, but haven\'t finished \
# submitting your documents for the insurance. To start driving, you still need to submit these documents: \n{} \
# Tap here to upload them: \
# {}'.format(kwargs['car_name'], kwargs['missing_docs_list'], kwargs['docs_upload_url'])
#         }


# class ThirdDocumentsReminderDriver(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'TEXT': _render_driver_reminder_body(
#                 'second_docs_reminder_driver.jade',
#                 kwargs['missing_docs_html'],
#             ),
#             'CTA_LABEL': 'Upload Documents Now',
#             'CTA_URL': kwargs['docs_upload_url'],
#             'HEADLINE': 'Don\'t forget to upload your documents for idlecars',
#             'template_name': 'one_button_no_image',
#             'subject': 'Are you ready to drive?',
#             'sms_body': 'Don\'t forget to upload your documents for idlecars. \
# You’ve successfully created an account, now you can upload your missing documents so it\'s easier to rent whenever you want: {}. \
# Tap here to upload now: {}'.format(kwargs['missing_docs_list'], kwargs['docs_upload_url']),
#         }


# class BookingTimedOut(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         if kwargs['driver_all_docs_uploaded']:
#             template = 'booking_timed_out_cc.jade'
#             subject = 'Your {} rental has been cancelled because you never checked out.'.format(
#                 kwargs['car_name']
#             )
#         else:
#             template = 'booking_timed_out.jade'
#             subject = 'Your rental has been cancelled because we don\'t have your driver documents.'

#         template_data = {
#             'CAR_NAME': kwargs['car_name'],
#         }

#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'TEXT': render_to_string(template, template_data, django_template.Context(autoescape=False)),
#             'CTA_LABEL': 'Find your car',
#             'CTA_URL': kwargs['car_listing_url'],
#             'HEADLINE': 'Your {} rental was canceled'.format(kwargs['car_name']),
#             'CAR_IMAGE_URL': kwargs['car_image_url'],
#             'template_name': 'one_button_one_image',
#             'subject': subject,
#             'sms_body': 'We\’re sorry. ' + subject + ' But don’t worry! You can always come back and find another car! \
# Tap here to find another car today: {}'.format(kwargs['car_listing_url']),
#         }


class AwaitingInsuranceEmail(notification.DriverNotification):
    def get_context(self, **kwargs):
        template_data = {
            'CAR_NAME': kwargs['car_name']
        }
        body = render_to_string("driver_docs_approved.jade", template_data, django_template.Context(autoescape=False))

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': body,
            'CTA_LABEL': 'See your car',
            'CTA_URL': kwargs['bookings_url'],
            'HEADLINE': 'Your documents have been submitted for approval',
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Congratulations! Your documents have been submitted!',
        }


# class FirstInsuranceNotification(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         subject = 'We are still working to get you on the {}’s insurance.'.format(kwargs['car_name'])
#         sms_body = 'Hi {}, we are still working to get you on the {}’s insurance. We will \
# let you know as soon as the car is ready for pickup.'.format(
#             kwargs['driver_first_name'] or None,
#             kwargs['car_name'],
#         )
#         text = '''We are still working to get you on the {}’s insurance. We will let you know
#         as soon as the car is ready for pickup.'''.format(
#             kwargs['car_name'],
#         )

#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'TEXT': text,
#             'HEADLINE': subject,
#             'template_name': 'no_button_no_image',
#             'subject': subject,
#             'sms_body': sms_body,
#         }


# class SecondInsuranceNotification(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         subject = 'We told the owner to get you on the insurance ASAP'
#         sms_body = 'Hi {}, we told the owner of the {} to get you on the insurance ASAP, \
# so you shouldn’t have to wait much longer!'.format(
#             kwargs['driver_first_name'] or None,
#             kwargs['car_name'],
#         )
#         text = 'We told the owner of the {} to get you on the insurance ASAP, so you shouldn’t \
#         have to wait much longer!'.format(
#             kwargs['car_name'],
#         )
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'TEXT': text,
#             'HEADLINE': subject,
#             'template_name': 'no_button_no_image',
#             'subject': subject,
#             'sms_body': sms_body,
#         }


# class InsuranceApproved(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         template_data = {
#             'CAR_NAME': kwargs['car_name'],
#         }
#         body = render_to_string("driver_insurance_approved.jade", template_data, django_template.Context(autoescape=False))

#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': 'You have been added to your car\'s insurance',
#             'CAR_IMAGE_URL': kwargs['car_image_url'],
#             'TEXT': body,
#             'CTA_LABEL': 'Pick up your car',
#             'CTA_URL': kwargs['bookings_url'],
#             'template_name': 'one_button_one_image',
#             'subject': 'Alright! Your {} is ready to pick up!'.format(kwargs['car_name']),
#             'sms_body': 'Congratulations! You have been approved to drive the {}!\
# How to pick up your car:\n\
# Tap here to go to My Rentals in the idlecars app: {}\n\
# Tap "Arrange to pick up your car".\n\
# Call the owner to schedule meet and pick up the car.\n\
# When you meet the owner, inspect the car and make sure it meets your expectations.\n\
# Follow the instructions in the app and click “Pay & Drive” to pay the first week\'s rent.\n\
# The owner will receive a notification, and give you the keys.\n\
# Need help? Contact us:\n\
# 1-844-IDLECAR (1-844-435-3227)'.format(kwargs['car_name'], kwargs['bookings_url'])
#         }


class InsuranceRejected(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = 'You couldn\'t be added to the car you wanted this time. But now that your \
account is complete, it\s easy to pick another car, and we\'ll get you on that one. '

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Sorry, you couldn\'t be added to the car you wanted.',
            'TEXT': text,
            'CTA_LABEL': 'Find another car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'You couldn\'t be added to the car you wanted',
        }


# class InsuranceFailed(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         text = 'We\'re sorry, but we were unable to get you in your {} due to an issue with \
# the owner. Your deposit has been fully refunded. We sincerely apologize for any inconvenience. \
# Now that your account is complete, you can pick another car and we\'ll start processing your \
# new rental immediately. '.format(kwargs['car_name'])
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': 'Sorry, We were unable to complete your rental.',
#             'TEXT': text,
#             'CTA_LABEL': 'Find a new car',
#             'CTA_URL': kwargs['car_listing_url'],
#             'template_name': 'one_button_no_image',
#             'subject': 'We were unable to complete your {} booking'.format(kwargs['car_name']),
#             'sms_body': text + kwargs['car_listing_url']
#         }


class CarRentedElsewhere(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = 'Sorry, someone else took the car you wanted. Sometimes that happens. Still, \
there are plenty more great cars available. '
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Sorry, the car you wanted was taken by someone else.',
            'TEXT': '''{}
            <br />
            <p>Need help? Contact us:</p>
            <p>drivers@alltaxiny.com </p>
            <p>'''.format(text) + settings.ALLTAXI_PHONE_NUMBER + '</p>',
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Sorry, someone else rented out the car you wanted.',
        }


# class CheckoutReceipt(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         text = '''We put a hold of ${} on your credit card. You will not be charged until \
# you inspect and approve the car in the app. When you pick up the car, the deposit will be \
# processed, and your card will be charged for the first week's rent. Your documents have \
# been submitted to the owner for insurance approval. You will be notified in 24-48 hours when \
# you are approved. If you have questions please contact {} at {}.'''.format(
#                 kwargs['car_deposit'],
#                 kwargs['owner_name'],
#                 fields.format_phone_number(kwargs['owner_phone_number']),
#             )
#         subject = 'Your {} was successfully reserved.'.format(kwargs['car_name'])
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': 'Your {} was successfully reserved'.format(kwargs['car_name']),
#             'TEXT': text,
#             'template_name': 'no_button_no_image',
#             'subject': subject,
#             'sms_body': subject + ' ' + text
#         }


# class InvitorReceivedCredit(notification.DriverNotification):
#     def custom_params_sets(self):
#         return ['credit']

#     def get_context(self, **kwargs):
#         text = '''
#             You just received ${} of rental credit because someone rented a car with
#             Idlecars and used your code! You now have ${} of Idlecars credit to use
#             towards your next Idlecars rental. <br />
#             If you are already driving, this amount will be taken off your next rental payment. <br />
#             If you haven’t rented with us yet, you can use this credit towards your next rental! <br />
#             <br />
#             Click below to see our current selection of cars
#         '''.format(kwargs['credit_amount_invitor'], kwargs['driver_credit'])
#         subject = 'You just received ${} of Idlecars rental credit'.format(kwargs['credit_amount_invitor'])
#         sms_body = 'Hi {}, someone signed up using your Idlecars referral code! \
# You just received ${} towards your next rental!'.format(
#             kwargs['driver_first_name'],
#             kwargs['credit_amount_invitor'],
#         )
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': subject,
#             'TEXT': text,
#             'CTA_LABEL': 'Find your car',
#             'CTA_URL': kwargs['car_listing_url'],
#             'template_name': 'one_button_no_image',
#             'subject': subject,
#             'sms_body': sms_body,
#         }


class SomeoneElseBooked(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = 'While we were waiting for you to finish uploading your documents, \
another driver took your {}. But don\'t worry, there are plenty more cars \
available. '.format(kwargs['car_name'])
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Someone else rented your car!',
            'TEXT': text,
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Someone else rented your {}.'.format(kwargs['car_name']),
        }


class BookingCanceled(notification.DriverNotification):
    def get_context(self, **kwargs):
        body = '''
            Your {} request has been canceled. Now you can go back to the All Taxi listings and choose another car!
        '''.format(kwargs['car_name'])

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': body,
            'CTA_LABEL': 'Find another car',
            'CTA_URL': kwargs['car_listing_url'],
            'HEADLINE': 'Your request has been canceled',
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Confirmation: Your request has been canceled.',
        }

# class DriverRemoved(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         text = '''The owner has removed you from their {}. We look \
# forward to serving you next time!'''.format(
#             kwargs['car_name'],
#         )

#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': 'Your request has been approved.',
#             'TEXT': text,
#             'template_name': 'no_button_no_image',
#             'subject': 'You\'re removed from the {}.'.format(kwargs['car_name']),
#             'sms_body': text,
#         }


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
            'subject': 'Reset your All Taxi password.',
        }


class PasswordResetConfirmation(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = 'If you didn\'t set your password, or if you think something funny is going \
on, please call us any time at ' + settings.ALLTAXI_PHONE_NUMBER + '.'
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'HEADLINE': 'Your account password has been set',
            'TEXT': text,
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Your All Taxi password has been set.',
        }


# class UseYourCredit(notification.DriverNotification):
#     def get_context(self, **kwargs):
#         subject = 'You have ${} to use towards your next rental'.format(kwargs['driver_credit'])
#         text = 'Don’t forget! You have ${} for your next rental. See our current car selection \
# here <br /> Click below to see our current selection! <br />'.format(kwargs['driver_credit'])
#         sms_body = 'Hi {} don’t forget that you have ${} for your next rental. \
#  See our current car selection here: {}'.format(
#                 kwargs['driver_first_name'],
#                 kwargs['driver_credit'],
#                 kwargs['car_listing_url'],
#             )

#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': subject,
#             'TEXT': text,
#             'CTA_LABEL': 'Find your car',
#             'CTA_URL': kwargs['car_listing_url'],
#             'template_name': 'one_button_no_image',
#             'subject': subject,
#             'sms_body': sms_body,
#         }


# class InactiveCredit(notification.DriverNotification):
#     def __init__(self, campaign_name, argument, *args):
#         super(InactiveCredit, self).__init__(campaign_name, argument)
#         self.credit = args[0]

#     def get_context(self, **kwargs):
#         text = '''
#             We haven’t seen you in a while! We’d like to help you out! <br />

#             We have gone ahead and applied a ${} credit to your account to be used towards your next rental.
#             To claim your cash, all you need to do is click the link below and complete a rental with Idlecars
#             and the money will be automatically deducted from your first week's rent. <br />

#             Click below to find a car.
#         '''.format(self.credit)
#         sms_body = 'Hi {}, we have given you ${} to use on your next rental! Click here to book a car and claim your cash. \
# Find a car here: {}'.format(
#             kwargs['driver_first_name'],
#             self.credit,
#             kwargs['car_listing_url'],
#         )

#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': 'Collect some Idle Cash',
#             'TEXT': text,
#             'CTA_LABEL': 'Find your car',
#             'CTA_URL': kwargs['car_listing_url'],
#             'template_name': 'one_button_no_image',
#             'subject': 'Let us give you cash towards your rental',
#             'sms_body': sms_body,
#         }


# class InactiveReferral(notification.DriverNotification):
#     def custom_params_sets(self):
#         return ['credit']

#     def get_context(self, **kwargs):
#         sms_body = 'Give your friends ${} of Idlecars credit  with code {} and get ${} for \
# every friend that rents a car with Idlecars: {}'.format(
#             kwargs['credit_amount_invitee'],
#             kwargs['credit_code'],
#             kwargs['credit_amount_invitor'],
#             kwargs['car_listing_url'],
#         )
#         text = '''
#             Need some extra money to help with your rental? Want to share some saving with your friends?  <br />
#             Now that you have an Idlecars account, you have the chance to save on your weekly rent.
#             Every time you refer another driver with the code below they will get ${} towards their
#             first rental and you will get ${} for each driver you refer -
#             that money will go towards your weekly rent! <br /> <br />
#             Your Code: {} <br /><br />
#             How it works:
#             <ul><li> Send the code to your friend
#                 <li> They rent a car with Idlecars </li>
#                 <li> We give you ${} to be used for your next payment </li></ul>
#             <br />
#             Don’t have a car yet? Click below to find one!
#         '''.format(
#             kwargs['credit_amount_invitee'],
#             kwargs['credit_amount_invitor'],
#             kwargs['credit_code'],
#             kwargs['credit_amount_invitor'],
#         )
#         return {
#             'FNAME': kwargs['driver_first_name'] or None,
#             'HEADLINE': ' Share some Idle Cash with your friends and save on your next rental',
#             'TEXT': text,
#             'CTA_LABEL': 'Find your car',
#             'CTA_URL': kwargs['car_listing_url'],
#             'template_name': 'one_button_no_image',
#             'subject': 'Share some Idle Cash with your friends and save on your next rental',
#             'sms_body': sms_body,
#         }
