# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

'''
This is a dictionary of template_name => merge_vars samples for testing.
'''

img_1_url = 'https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-110c2125-1d5d-453c-9fdc-910e2418eb16-image.jpg'
img_2_url = 'https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-ab26e9c5-0f13-4750-96ad-d17079187164-IMG_1709.JPG'
img_3_url = 'https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-f7b6b0d4-b1f3-48ba-8db5-3ba73c476aca-image.jpg'
img_4_url = 'https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-011d18c7-47cb-455b-a5b6-56a8c2dc9729-IMAG0574.jpg'
img_5_url = 'https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-110c2125-1d5d-453c-9fdc-910e2418eb16-image.jpg'

merge_vars = {
    'no_button_no_image': {u'reynolds.tremaine@gmail.com': {u'FNAME': u'Davian',
                                  u'HEADLINE': u'Payment received for your 2012 Schmitt Walker',
                                  u'TEXT': u'\n        You have received a payment through idlecars. <br />\n        Invoice Period: Oct 10 - Oct 12 <br />\n        Payment Amount: $214.29\n        For your 2012 Schmitt Walker with medallion FYSXY1J6 <br />\n        From Driver: Olar Weimann <br />\n        <br /><br /><br />\n    This is the last payment. The driver should contact you to arrange dropoff.<br />\n        This booking will end on: Oct 12 <br /><br />\n        As always, if you have any questions, please call us at 1-844-IDLECAR (1-844-435-3227).\n    '}},
    'one_button_one_image': {
        'jeremy@idlecars.com': {
            'FNAME': 'Bob',
            'TEXT': "<p>Don't forget! To rent your 2014 Toyota Camry you still need to upload:</p>\n<ul><li>your Drivers License, and<li>your TLC License</ul>\n<p>You can also email photographs of your documents to support@idlecars.com. Once we have all your documents, you will be added to the car's insurance. Then you can start driving and start earning!</p>",
            'CTA_LABEL': 'Renew Now',
            'CTA_URL': 'http://idlecars.com',
            'HEADLINE': 'Your 2015 Rolls Royce is about to expire',
            'CAR_IMAGE_URL': 'https://s3.amazonaws.com/images.idlecars.com/lincoln_towncar.jpg',
        },
    },
    'one_button_no_image': {
        'jeremy@idlecars.com': {
            'CTA_LABEL': 'List more cars',
            'CTA_URL': 'http://goo.gl/forms/4s26I6GUQY',
            'FNAME': 'Lindell',
            'HEADLINE': 'Your bank account has been approved',
            'TEXT': '''Congrats! Your bank information has been approved and your cars have been listed!\nYou can view your live cars from the links below!\n
                <ul>
                <li><a href=http://localhost:3000/#/cars/3>\n\thttp://localhost:3000/#/listings/3\n</A>\n
                <li><a href=http://localhost:3000/#/cars/3>\n\thttp://localhost:3000/#/listings/1\n</A>\n
                </ul>\n
                If you have any other cars you would like to list, please go to the submission form here:\n'''
        }
    },
    'one_button_three_images': {
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
            'TEXT5': 'this is the text at the end of the email Maybe a wind-up for the call-to-action.',
            'CTA_LABEL': 'Press the button',
            'CTA_URL': 'http://idlecars.com',
        },
    },
    'one_button_four_images': {
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
    },
    'no_button_five_images': {
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
            'IMAGE_5_URL': img_5_url,
            'TEXT5': 'Caption for <a href="{}">image #4.</a>'.format(img_5_url),
            'TEXT6': 'this is the text at the end of the email Maybe a wind-up for the call-to-action.',
        },
    },
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
