# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from djrill.exceptions import MandrillAPIError

from idlecars import email
from owner_crm.tests.sample_merge_vars import merge_vars

class Command(BaseCommand):
    help = '''
    This command will iterate over all the template merge variable data and make sure
    that they match with the templates stored in Mandrill.
    '''

    def handle(self, *args, **options):
        for template in merge_vars.keys():
            self.test_template(template, merge_vars[template])
            self.stdout.write('.')
        return "\nFinished"

    def test_template(self, template, merge_vars):
        try:
            msg = email.send_sync('single_cta', "testing cross-Mandrill sending", merge_vars)
        except MandrillAPIError as e:
            self.report_error(unicode(e))
            return

        for result in msg.mandrill_response:
            if result['reject_reason']:
                self.report_error(result['reject_reason'])

    def report_error(self, error_message):
        self.stdout.write('\nERROR: {}\n'.format(error_message))
