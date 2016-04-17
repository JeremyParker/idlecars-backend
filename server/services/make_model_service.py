# -*- encoding:utf-8 -*-
from __future__ import unicode_literals


def get_image_url(make_model, key=0):
    '''
    Returns an image for the given make/model using id as a hash key.
    Always returns the same image for the same key
    '''
    if not make_model.image_filenames:
        return None

    images = make_model.image_filenames.split(',')
    ix = key % len(images)

    return 'https://e062aa70f155542638848b75d5d43e15fbc73a56.googledrive.com/host/0B1HbewCnXlPic3JEb3B6dHEycTg/{}'.format(images[ix].strip())
