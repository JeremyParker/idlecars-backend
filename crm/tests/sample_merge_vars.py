# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

'''
This is a dictionary of template_name => merge_vars samples for testing.
'''

merge_vars = {
    'single_cta': {
        'jeremy@idlecars.com': {
            'FNAME': '',
            'TEXT': 'test',
            'CTA_LABEL': 'Click Here',
            'CTA_URL': 'http://idlecars.com',
        },
    },
    'owner_renewal': {
        'jeremy@idlecars.com': {
            'FNAME': 'Bob',
            'TEXT': 'a bunch of text',
            'CTA_LABEL': 'Renew Now',
            'CTA_URL': 'http://idlecars.com',
            'HEADLINE': 'Your 2015 Rolls Royce is about to expire',
            'CAR_IMAGE_URL': 'https://s3.amazonaws.com/images.idlecars.com/lincoln_towncar.jpg',
        },
    },
}


def check_template_keys(outbox):
    '''
    Returns true if all emails in the given outbox have the correct keys for their template
    '''
    template_dict = merge_vars[outbox[0].template_name]
    expected_keys = set(template_dict.values()[0])
    for message in outbox:
        email = message.merge_vars.keys()[0]
        var = message.merge_vars[email]
        if set([]) != set(var.keys()) - expected_keys:
            return False;
    return True
