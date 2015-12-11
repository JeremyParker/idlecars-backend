# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

# don't import the class or the test will find it and try to test it as a notification.
from django import template
from django.template.loader import render_to_string
from django.conf import settings

from idlecars import email, app_routes_driver, app_routes_owner
from server.services import car as car_service

from owner_crm.models import notification


def _get_car_listing_links(owner):
    links = ''
    for car in car_service.filter_live(owner.cars.all()):
        car_url = app_routes_driver.car_details_url(car)
        links = links + '<li><a href={}>\n\t{}\n</A>\n'.format(car_url, car_url)
    return links


def _render_renewal_body(**kwargs):
    template_data = {
        'CAR_NAME': kwargs['car_name'],
        'CAR_PLATE': kwargs['car_plate'],
    }
    context = template.Context(autoescape=False)
    return render_to_string("car_expiring.jade", template_data, context)


class RenewalEmail(notification.OwnerNotification):
    def get_context(self, **kwargs):
        body = _render_renewal_body(**kwargs)

        context = {
            'FNAME': kwargs.get('user_first_name', None),
            'HEADLINE': 'Your {} listing is about to expire'.format(kwargs['car_name']),
            'TEXT': body,
            'CTA_LABEL': 'Update Listing Now',
            'CTA_URL': kwargs['car_owner_details_url'],
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Your {} listing is about to expire.'.format(kwargs['car_name']),
            'sms_body': 'The listing for your {} with license plate {} is about to expire. \
Is it still available? Please tap here to extend or remove your \
listing: {}'.format(kwargs['car_name'], kwargs['car_plate'], kwargs['car_owner_details_url'])
        }
        return context


class NewBookingEmail(notification.OwnerNotification):
    def get_context(self, **kwargs):
        headline = '{} has booked your {}, with license plate {}'.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        # TODO(JP) track gender of driver and customize this email text
        text = '''
            {} has booked your car and has paid the ${} deposit.
            Please have them added to the insurance policy today to ensure that they can start driving tomorrow.
            All of their documents are included in this email.
        '''.format(kwargs['driver_first_name'], kwargs['car_deposit'])

        context = {
            'PREVIEW': headline,
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': headline,
            'TEXT0': text,
            'IMAGE_1_URL': kwargs['driver_license_image'],
            'TEXT1': 'DMV License <a href="{}">(click here to download)</a>'.format(
                kwargs['driver_license_image']
            ),
            'IMAGE_2_URL': kwargs['fhv_license_image'],
            'TEXT2': 'FHV/Hack License <a href="{}">(click here to download)</a>'.format(
                kwargs['fhv_license_image']
            ),
            'IMAGE_3_URL': kwargs['defensive_cert_image'],
            'TEXT3': 'Defensive Driving Certificate <a href="{}">(click here to download)</a>'.format(
                kwargs['defensive_cert_image']
            ),
            'IMAGE_4_URL': kwargs['address_proof_image'],
            'TEXT4': 'Proof of address <a href="{}">(click here to download)</a>'.format(
                kwargs['address_proof_image']
            ),
            'IMAGE_5_URL': kwargs['base_letter'],
            'TEXT5': 'Base letter <a href="{}">(click here to download)</a>'.format(
                kwargs['base_letter']
            ),
            'TEXT6': 'Questions? Call us at ' + settings.IDLECARS_PHONE_NUMBER,
            'subject': 'A driver has booked your {}.'.format(kwargs['car_name']),
            'template_name': 'no_button_five_images',
            'sms_body': headline + ' An email has been sent to {} with more information.'.format(
                kwargs['user_email']
            )
        }
        return context


class FirstMorningInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        text = 'We are just checking in on {}\'s {} rental with plate \
{} to see if they have been accepted on the insurance. You can call the number below to let us \
know where they are in the process. Once they are approved, they will contact you to schedule \
a pickup. '.format(kwargs['driver_full_name'], kwargs['car_name'], kwargs['car_plate'])
        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': text,
            'CTA_LABEL': 'Call (844) 435-3227',
            'CTA_URL': 'tel:1-844-4353227',
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'sms_body': text + '\nCall (844) 435-3227'
        }


class SecondMorningInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        text = 'We are doing a final checks on {} {} rental with plate {} to see if \
they have been accepted on the insurance. You can call the number below to let us know where \
they are in the process. Once they are approved, they will contact you to schedule a pickup. \
We promise drivers that they will get into a car within 24-48 hours, so if we don’t hear \
back we will have to cancel the rental. We don’t want to do that so please let us know if \
there are any problems.'.format(kwargs['driver_full_name'], kwargs['car_name'], kwargs['car_plate'])

        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'The {} rental for {} will be cancelled soon'.format(kwargs['car_name'], kwargs['driver_full_name']),
            'TEXT': '''
                We are doing a final checks on {} {} rental with plate
                {} to see if they have been accepted on the insurance.
                You can click below to let us know where they are in the process.
                Once they are approved, they will contact you to schedule a pickup.
                <br />
                We promise drivers that they will get into a car within 24-48 hours,
                so if we don’t hear back we will have to cancel the rental.
                We don’t want to do that so please let us know if there are any problems.
            '''.format(kwargs['driver_full_name'], kwargs['car_name'], kwargs['car_plate']),
            'CTA_LABEL': 'Call (844) 435-3227',
            'CTA_URL': 'tel:1-844-4353227',
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'sms_body': text + '\nCall (844) 435-3227',
        }


class FirstAfternoonInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        text = 'We\'re just checking in on {}\'s {} rental with plate \
{} to see if they have been accepted on the insurance. You can click below to \
let us know where they are in the process. Once they are approved, they will \
contact you to schedule a pickup.'.format(kwargs['driver_full_name'], kwargs['car_name'], kwargs['car_plate'])

        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': '''
                We are just checking in on {} {} rental with plate
                {} to see if they have been accepted on the insurance.
                You can click below to let us know where they are in the process.
                Once they are approved, they will contact you to schedule a pickup.
            '''.format(kwargs['driver_full_name'], kwargs['car_name'], kwargs['car_plate']),
            'CTA_LABEL': 'Call (844) 435-3227',
            'CTA_URL': 'tel:1-844-4353227',
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'sms_body': text,
        }


class SecondAfternoonInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        text = 'We\'re doing a final checks on {}\'s {} rental with plate {} to see if they have \
been accepted on the insurance. You can click below to let us know where they are in the process. \
Once they are approved, they will contact you to schedule a pickup. We promise drivers that they \
will get into a car within 24-48 hours, so if we don’t hear back we will have to cancel the rental. \
We don’t want to do that so please let us know if there are any problems.'.format(
    kwargs['driver_full_name'],
    kwargs['car_name'],
    kwargs['car_plate']
)

        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'The {} rental for {} will be cancelled soon'.format(kwargs['car_name'], kwargs['driver_full_name']),
            'TEXT': '''
                We are doing a final checks on {} {} rental with plate
                {} to see if they have been accepted on the insurance.
                You can click below to let us know where they are in the process.
                Once they are approved, they will contact you to schedule a pickup.
                <br />
                We promise drivers that they will get into a car within 24-48 hours,
                so if we don’t hear back we will have to cancel the rental.
                We don’t want to do that so please let us know if there are any problems.
            '''.format(kwargs['driver_full_name'], kwargs['car_name'], kwargs['car_plate']),
            'CTA_LABEL': 'Call (844) 435-3227',
            'CTA_URL': 'tel:1-844-4353227',
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'sms_body': text,
        }


class PickupConfirmation(notification.OwnerNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': '{} has paid you for the {}'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': '''
                You have received a payment of ${} from {} for the {}
                You can now give them the keys to drive.
                <br />
                Their credit card has been charged and you will receive the payment within 48 hours. The security
                deposit of ${} has also been placed in escrow for you.
            '''.format(
                # TODO: not always weely_rent_amount, we need to get the real amount, if time < 7 days
                kwargs['booking_weekly_rent'],
                kwargs['driver_full_name'],
                kwargs['car_name'],
                kwargs['car_deposit']
            ),
            'template_name': 'no_button_no_image',
            'subject': '{} has paid you for the {}'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'sms_body': 'You have received a payment of ${} from {} for the {} You can now give them \
the keys to drive. Their credit card has been charged and you will receive the payment within 48 hours. \
The security deposit of ${} has also been placed in escrow for you.'.format(
                # TODO: not always weely_rent_amount, we need to get realy amount, if time < than 7days
                kwargs['booking_weekly_rent'],
                kwargs['driver_full_name'],
                kwargs['car_name'],
                kwargs['car_deposit']
            )
        }


class PaymentReceipt(notification.OwnerNotification):
    def get_context(self, **kwargs):
        text = '''
            You have received a payment through idlecars. <br /><br />
            Car: {} with license plate {} <br />
            Driver: {} <br /><br />

            Invoice Period: {} - {} <br />
            Payment Amount: ${} <br />
            Service Fee: ${} <br />
            ---------------------------------- <br />
            Total disbursement: ${} <br /><br />
        '''.format(
                kwargs['car_name'],
                kwargs['car_plate'],
                kwargs['driver_full_name'],

                kwargs['payment_invoice_start_time'].strftime('%b %d'),
                kwargs['payment_invoice_end_time'].strftime('%b %d'),
                kwargs['payment_cash_amount'] + kwargs['payment_credit_amount'],
                kwargs['payment_service_fee'],
                kwargs['payment_amount'] - kwargs['payment_service_fee'],
            )

        if kwargs['payment_credit_amount'] > 0:
            text += '''
                Due to an Idlecars promotion we are covering a portion of the driver’s rent.
                This will cause the payment to come in two separate deposits at the same time: <br />
                Payment 1: ${} <br />
                Payemnt 2: ${} <br />
                <br />
            '''.format(
                kwargs['payment_cash_amount'],
                kwargs['payment_credit_amount'],
            )

        if kwargs['booking_next_payment_amount'] > 0:
            text += 'The next payment of ${} will occur on {} <br />'.format(
                kwargs['booking_next_payment_amount'],
                kwargs['booking_invoice_end_time'].strftime('%b %d')
            )
        else:
            text += 'This is the last payment. The driver should contact you to arrange dropoff.<br />'

        text += '''
            This rental will end on: {} <br /><br />
            As always, if you have any questions, please call us at {}.<br />
            Thank you.
        '''.format(
            kwargs['booking_end_time'].strftime('%b %d'),
            settings.IDLECARS_PHONE_NUMBER,
        )

        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': 'Payment received for your {}'.format(kwargs['car_name']),
            'TEXT': text,
            'template_name': 'no_button_no_image',
            'subject': 'Payment receipt from idlecars rental: {} license plate {}'.format(
                kwargs['car_name'],
                kwargs['car_plate'],
            ),
        }


class BookingCanceled(notification.OwnerNotification):
    def get_context(self, **kwargs):
        headline = '{} has decided not to rent your {}, with license plate {}'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        text = 'We\'re sorry. {} has decided not to rent your {}. Could you ask your insurance \
broker not to add them to the insurance policy? We apologise for any inconvenience. We\'ve \
already re-listed your car on the site so we can find you another driver as soon as possible.'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
        )
        # TODO(JP) track gender of driver and customize this email text
        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': headline,
            'TEXT': text,
            'CTA_LABEL': 'See your listing',
            'CTA_URL': kwargs['car_driver_details_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Your {} rental has canceled.'.format(kwargs['car_name']),
            'sms_body': text,
        }


class DriverRejected(notification.OwnerNotification):
    def get_context(self, **kwargs):
        headline = '{} has decided not to rent your {}, with license plate {}'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        text = 'We\'re sorry. {} has decided not to rent your {}. We apologise for any inconvenience. \
We\'ve already re-listed your car on the site so we can find you another driver as soon as possible.'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
        )
        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': headline,
            'TEXT': text,
            'CTA_LABEL': 'See your listing',
            'CTA_URL': kwargs['car_driver_details_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Your {} rental has canceled.'.format(kwargs['car_name']),
            'sms_body': text,
        }


class InsuranceTooSlow(notification.OwnerNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'Your {} rental has been canceled'.format(kwargs['car_name']),
            'TEXT': '''
                We are sorry to inform you, but we cancelled the {} rental for {}.
                We require drivers get on the insurance and into cars within 24 to 48 hours,
                so we hope that we will be able to do this next time.
                <br />
                If you are unsatisfied with your broker - please contact us to be added to our preferred broker list.
            '''.format(kwargs['car_name'], kwargs['driver_full_name']),
            'template_name': 'no_button_no_image',
            'subject': 'Your {} rental has been canceled'.format(kwargs['car_name']),
        }


class AccountCreated(notification.OwnerNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'CTA_URL': kwargs['owner_password_reset_url'],
            'template_name': 'owner_account_invite',
            'subject': 'Complete your account today - sign up with your bank account and start getting paid',
        }


class PasswordReset(notification.OwnerNotification):
    def get_context(self, **kwargs):
        text = 'We\'ve received a request to reset your password. If you didn\'t make the request, just \
ignore this message. Otherwise, you can reset your password using this link: '
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'HEADLINE': 'Reset your password',
            'TEXT': text,
            'CTA_LABEL': 'Reset password',
            'CTA_URL': kwargs['owner_password_reset_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Reset your idlecars password.',
            'sms_body': text + kwargs['owner_password_reset_url'],
        }


class PasswordResetConfirmation(notification.OwnerNotification):
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


class BankAccountApproved(notification.OwnerNotification):
    def get_context(self, **kwargs):
        links = _get_car_listing_links(kwargs['owner'])
        if links:
            text = '''
                    Congrats! Your bank information has been approved and your cars have been listed!
                    You can view your live cars from the links below!
                    <ul>{}</ul>
                    If you have any other cars you would like to list, please go to the submission form here:
                '''.format(links)
        else:
            text = '''
                    Congrats! Your bank information has been approved! Now when you rent cars through idlecars, you will
                    receive payment directly from the driver into your bank account.<br>
                    If you have any cars you would like to list, please go to the submission form here:
                '''

        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'Your bank account has been approved',
            'TEXT': text,
            'CTA_LABEL': 'List more cars',
            'CTA_URL': app_routes_owner.owner_app_url(),
            'template_name': 'one_button_no_image',
            'subject': 'Your bank account has been approved.',
        }
