# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

'''
This is a dictionary of template_name => merge_vars samples for testing.
'''

img_1_url = 'https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-110c2125-1d5d-453c-9fdc-910e2418eb16-image.jpg'
img_2_url = 'https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-ab26e9c5-0f13-4750-96ad-d17079187164-IMG_1709.JPG'
img_3_url = 'https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-f7b6b0d4-b1f3-48ba-8db5-3ba73c476aca-image.jpg'
img_4_url = 'https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-011d18c7-47cb-455b-a5b6-56a8c2dc9729-IMAG0574.jpg'

merge_vars = {
    'single_cta': {  # deprecated
        'jeremy@idlecars.com': {
            'FNAME': '',
            'TEXT': 'test',
            'CTA_LABEL': 'Click Here',
            'CTA_URL': 'http://idlecars.com',
        },
    },
    'one_button_one_image': {
        'jeremy@idlecars.com': {
            'FNAME': 'Bob',
            'TEXT': 'a bunch of text that explains what the hell is going on.',
            'CTA_LABEL': 'Renew Now',
            'CTA_URL': 'http://idlecars.com',
            'HEADLINE': 'Your 2015 Rolls Royce is about to expire',
            'CAR_IMAGE_URL': 'https://s3.amazonaws.com/images.idlecars.com/lincoln_towncar.jpg',
        },
    },
    'one_button_no_image': {
        'jeremy@idlecars.com': {
            'FNAME': 'Robert',
            'HEADLINE': 'Welcome to the End Of The World!',
            'TEXT': 'have lunch with me',
            'CTA_LABEL': 'Press a button',
            'CTA_URL': 'http://idlecars.com',
        },
    },
    'one_button_four_images': {
        'jeremy@idlecars.com': {
            'PREVIEW': 'Small text that shows you a peek of the content from your email list view.',
            'FNAME': 'Robert',
            'HEADLINE': 'We have a better sandwich!',
            'TEXT0': 'this is the intro text. Please note that the intro text looks really good.',
            'TEXT1': 'Caption for image #1',
            'TEXT2': 'Caption for image #2.',
            'TEXT3': 'Caption for image #3.',
            'TEXT4': 'Caption for image #4.',
            'TEXT5': 'this is the text at the end of the email Maybe a wind-up for the call-to-action.',
            'CTA_LABEL': 'Press the button',
            'CTA_URL': 'http://idlecars.com',
        },
    },
    'no_button_four_images': {
        'jeremy@idlecars.com': {
            'PREVIEW': 'Small text that shows you a peek of the content from your email list view.',
            'FNAME': 'Robert',
            'HEADLINE': 'We have a better sandwich!',
            'TEXT0': 'this is the intro text. Please note that the intro text looks really good.',
            'IMAGE_1_URL': img_1_url,
            'TEXT1': 'Caption for <a href="{}">image #1.</a>'.format(img_1_url),
            'IMAGE_2_URL': img_2_url,
            'TEXT2': 'Caption for <a href="{}">image #2.</a>'.format(img_2_url),
            'IMAGE_3_URL': img_3_url,
            'TEXT3': 'Caption for <a href="{}">image #3.</a>'.format(img_3_url),
            'IMAGE_4_URL': img_4_url,
            'TEXT4': 'Caption for <a href="{}">image #4.</a>'.format(img_4_url),
            'TEXT5': 'this is the text at the end of the email Maybe a wind-up for the call-to-action.',
        },
    }
}


def check_template_keys(outbox):
    '''
    Returns true if all emails in the given outbox have the correct keys for their template
    '''
    for message in outbox:
        template_dict = merge_vars[message.template_name]
        expected_keys = set(template_dict.values()[0])
        email = message.merge_vars.keys()[0]
        var = message.merge_vars[email]
        if set([]) != set(var.keys()) - expected_keys:
            print 'Different merge fields: {}'.format(set(var.keys()) - expected_keys)
            return False;
    return True
