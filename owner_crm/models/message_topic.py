# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

''' Used to track every object that can be used as a key for communication. '''

class MessageTopic(models.Model):
    pass

class MessageTopicModel(models.Model):
    class Meta:
        abstract = True

    topic_object = models.OneToOneField(MessageTopic, null=True) # default=MessageTopic.objects.create())
