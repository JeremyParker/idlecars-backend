# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# from server.models import Driver, Owner, Booking, Car
from owner_crm.models.message_topic import MessageTopic

class Message(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    campaign = models.CharField(max_length = 255)

    # what object was this message "about"
    message_topic = models.ForeignKey(MessageTopic, null=True)

    # owner = models.ForeignKey(Owner, blank=True, null=True)
    # car = models.ForeignKey(Car, blank=True, null=True)
    # driver = models.ForeignKey(Driver, blank=True, null=True)
    # booking = models.ForeignKey(Booking, blank=True, null=True)

    # TODO: also store what media of message this was: email or sms

    '''
    TODO: maybe try making every model have a one-to-one relationship with a generic Object table.
    Then Message can have a generic_object rather than owner, car, driver, ...etc. Then the filter
    can use:
    recipient_objects = Booking.objects.exclude(
        generic_object__message__campaign='my_campaign'
    )

    TODO: maybe try to use a GenericForeignKey like:
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.contrib.contenttypes.models import ContentType

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    ... then inject a subquery when finding the objects to send messages about.
    qs = Result.objects.extra(where = ["NOT EXISTS(SELECT * FROM myapp_result as T2 WHERE (T2.test_type_id = myapp_result.test_type_id AND T2.subject_id = myapp_result.subject ID AND T2.time > myapp_result.time))"])
    '''
