# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.template import Context
from django.template.loader import render_to_string
from django.conf import settings

from idlecars import email, client_side_routes
from server.services import car as car_service

from owner_crm.models import notification


def _get_car_listing_links(owner):
    links = ''
    for car in car_service.filter_live(owner.cars.all()):
        car_url = client_side_routes.car_details_url(car)
        links = links + '<li><a href={}>\n\t{}\n</A>\n'.format(car_url, car_url)
    return links


def _render_renewal_body(**kwargs):
    template_data = {
        'CAR_NAME': kwargs['car_name'],
        'CAR_PLATE': kwargs['car_plate'],
    }
    context = Context(autoescape=False)
    return render_to_string("car_expiring.jade", template_data, context)


class RenewalEmail(notification.OwnerNotification):
    def get_context(self, **kwargs):
        body = _render_renewal_body(**kwargs)

        context = {
            'FNAME': kwargs.get('user_first_name', None),
            'HEADLINE': 'Your {} listing is about to expire'.format(kwargs['car_name']),
            'TEXT': body,
            'CTA_LABEL': 'Renew Listing Now',
            'CTA_URL': kwargs['renewal_url'],
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Your {} listing is about to expire.'.format(kwargs['car_name']),
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
        }
        return context


class FirstMorningInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': '''
                We are just checking in on {} {} booking with plate
                {} to see if they have been accepted on the insurance.
                You can click below to let us know where they are in the process.
                Once they are approved, they will contact you to schedule a pickup.
            '''.format(kwargs['driver_full_name'], kwargs['car_name'], kwargs['car_plate']),
            'CTA_LABEL': 'Call (844) 435-3227',
            'CTA_URL': 'tel:1-844-4353227',
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
        }


class SecondMorningInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'The {} booking for {} will be cancelled soon'.format(kwargs['car_name'], kwargs['driver_full_name']),
            'TEXT': '''
                We are doing a final checks on {} {} booking with plate
                {} to see if they have been accepted on the insurance.
                You can click below to let us know where they are in the process.
                Once they are approved, they will contact you to schedule a pickup.
                <br />
                We promise drivers that they will get into a car within 24-48 hours,
                so if we don’t hear back we will have to cancel the booking.
                We don’t want to do that so please let us know if there are any problems.
            '''.format(kwargs['driver_full_name'], kwargs['car_name'], kwargs['car_plate']),
            'CTA_LABEL': 'Call (844) 435-3227',
            'CTA_URL': 'tel:1-844-4353227',
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
        }


class FirstAfternoonInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': '''
                We are just checking in on {} {} booking with plate
                {} to see if they have been accepted on the insurance.
                You can click below to let us know where they are in the process.
                Once they are approved, they will contact you to schedule a pickup.
            '''.format(kwargs['driver_full_name'], kwargs['car_name'], kwargs['car_plate']),
            'CTA_LABEL': 'Call (844) 435-3227',
            'CTA_URL': 'tel:1-844-4353227',
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
        }


class SecondAfternoonInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'The {} booking for {} will be cancelled soon'.format(kwargs['car_name'], kwargs['driver_full_name']),
            'TEXT': '''
                We are doing a final checks on {} {} booking with plate
                {} to see if they have been accepted on the insurance.
                You can click below to let us know where they are in the process.
                Once they are approved, they will contact you to schedule a pickup.
                <br />
                We promise drivers that they will get into a car within 24-48 hours,
                so if we don’t hear back we will have to cancel the booking.
                We don’t want to do that so please let us know if there are any problems.
            '''.format(kwargs['driver_full_name'], kwargs['car_name'], kwargs['car_plate']),
            'CTA_LABEL': 'Call (844) 435-3227',
            'CTA_URL': 'tel:1-844-4353227',
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
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
                # TODO: not always weely_rent_amount, we need to get realy amount, if time < than 7days
                kwargs['booking_weekly_rent'],
                kwargs['driver_full_name'],
                kwargs['car_name'],
                kwargs['car_deposit']
            ),
            'template_name': 'no_button_no_image',
            'subject': '{} has paid you for the {}'.format(kwargs['driver_full_name'], kwargs['car_name']),
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
            Total disbursement: ${} <br />
            <br /><br />
        '''.format(
                kwargs['car_name'],
                kwargs['car_plate'],
                kwargs['driver_full_name'],

                kwargs['payment_invoice_start_time'].strftime('%b %d'),
                kwargs['payment_invoice_end_time'].strftime('%b %d'),
                kwargs['payment_amount'],
                kwargs['payment_service_fee'],
                kwargs['payment_amount'] - kwargs['payment_service_fee'],
            )

        from server.services import booking as booking_service
        fee, amount, start_time, end_time = booking_service.calculate_next_rent_payment(kwargs['booking'])
        if amount > 0:
            text += 'The next payment of ${} will occur on {} <br />'.format(amount, end_time.strftime('%b %d'))
        else:
            text += 'This is the last payment. The driver should contact you to arrange dropoff.<br />'

        text += '''
            This booking will end on: {} <br /><br />
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

        text = '''We're sorry. {} has decided not to rent your {}. Could you ask your insurance
        broker not to add them to the insurance policy? We apologise for any inconvenience. We've
        already re-listed your car on the site so we can find you another driver as soon as possible.
        '''.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
        )
        # TODO(JP) track gender of driver and customize this email text
        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': headline,
            'TEXT': text,
            'CTA_LABEL': 'See your listing',
            'CTA_URL': client_side_routes.car_details_url(kwargs['car']),
            'template_name': 'one_button_no_image',
            'subject': 'Your {} booking has canceled.'.format(kwargs['car_name']),
        }


class DriverRejected(notification.OwnerNotification):
    def get_context(self, **kwargs):
        headline = '{} has decided not to rent your {}, with license plate {}'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        text = '''We're sorry. {} has decided not to rent your {}. We apologise for any inconvenience.
        We've already re-listed your car on the site so we can find you another driver as soon as possible.
        '''.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
        )
        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': headline,
            'TEXT': text,
            'CTA_LABEL': 'See your listing',
            'CTA_URL': client_side_routes.car_details_url(kwargs['car']),
            'template_name': 'one_button_no_image',
            'subject': 'Your {} booking has canceled.'.format(kwargs['car_name']),
        }


class InsuranceTooSlow(notification.OwnerNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'Your {} booking has been canceled'.format(kwargs['car_name']),
            'TEXT': '''
                We are sorry to inform you, but we cancelled the {} booking for {}
                We require drivers get on the insurance and into cars within 24 to 48 hours,
                so we hope that we will be able to do this next time.
                <br />
                If you are unsatisfied with your broker - please contact us to be added to our preferred broker list.
            '''.format(kwargs['car_name'], kwargs['driver_full_name']),
            'template_name': 'no_button_no_image',
            'subject': 'Your {} booking has been canceled'.format(kwargs['car_name']),
        }


def account_created(password_reset):
    if not password_reset.auth_user.email:
        return  # TODO - send some sort of error email, or at least log the error.
    merge_vars = {
        password_reset.auth_user.email: {
            'FNAME': password_reset.auth_user.first_name or None,
            'CTA_URL': client_side_routes.owner_password_reset(password_reset),
        }
    }
    email.send_async(
        template_name='owner_account_invite',
        subject='Complete your account today - sign up with your bank account and start getting paid',
        merge_vars=merge_vars,
    )


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
            'CTA_URL': client_side_routes.add_car_form(),
            'template_name': 'one_button_no_image',
            'subject': 'Your bank account has been approved.',
        }
