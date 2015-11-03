# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from idlecars import email

from owner_crm.models import Campaign


class Notification(object):
    def __init__(self, campaign_name, argument):
        self.campaign_name = campaign_name
        self.argument = argument

    def get_channel(self, receiver):
        try:
            campaign = Campaign.objects.get(name=self.campaign_name)
        except Campaign.DoesNotExist:
            campaign = Campaign.objects.create(name=self.campaign_name)

        if campaign.preferred_medium is Campaign.SMS_MEDIUM and receiver['sms_enabled']:
            return Campaign.SMS_MEDIUM
        else:
            return Campaign.EMAIL_MEDIUM

    def send(self):
        def _get_merge_vars():
            return {
                'FNAME': context['FNAME'],
                'HEADLINE': context['HEADLINE'],
                'TEXT': context['TEXT'],
                'CTA_LABEL': context['CTA_LABEL'],
                'CTA_URL': context['CTA_URL'],
            }

        context = self.get_context()

        import pdb; pdb.set_trace()

        for receiver in self.get_all_receivers():
            if self.get_channel(receiver) is Campaign.SMS_MEDIUM:
                pass
            else:
                if not receiver['email_address']:
                    return

                merge_vars = {receiver['email_address']: _get_merge_vars()}

                email.send_async(
                    template_name=context['template_name'],
                    subject=context['subject'],
                    merge_vars=merge_vars,
                )

    def get_all_receivers(self):
        clas = type(self.argument).__name__

        if clas == 'Driver':
            receiver = self.argument
            return [{'email_address': receiver.email(), 'sms_enabled': receiver.sms_enabled}]
        elif clas == 'Owner':
            pass
        elif clas == 'Booking':
            receivers = self.argument.car.owner.auth_users.all()
            return [{'email_address': receiver.email, 'sms_enabled': receiver.sms_enabled} for receiver in receivers]
        elif clas == 'Payment':
            receivers = self.argument.booking.car.owner.auth_users.all()
            return [{'email_address': receiver.email, 'sms_enabled': receiver.sms_enabled} for receiver in receivers]
        else:
            pass


class DriverNotification(Notification):
    pass


class OwnerNotification(Notification):
    pass


class OpsNotification(Notification):
    def get_all_receivers(self):
        # TODO: get sms_enabled from settings
        return [{'email_address': settings.OPS_EMAIL, 'sms_enabled': False}]


class StreetTeamNotification(Notification):
    def get_all_receivers(self):
        # TODO: get sms_enabled from settings
        return [{'email_address': settings.STREET_TEAM_EMAIL, 'sms_enabled': False}]


