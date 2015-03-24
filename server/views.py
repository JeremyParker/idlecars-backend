# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import JsonResponse
from django.http import HttpResponse

import sendgrid

# TODO: get this outa this file
class SendgridEmail:

    def __init__(self):
        # TODO: move this to env variable, duh
        self.sg = sendgrid.SendGridClient('app34610252@heroku.com', 'li2zhict')

    def send_to(self, address):
        message = sendgrid.Mail()
        message.add_to(address)
        message.set_subject('Welcome to idlecars')
        message.set_html('<h1>This is a test</h1>')
        message.set_text('This is a test')
        message.set_from('idlecars <info@idlecars.com>')
        return self.sg.send(message)

def index(request):
    return JsonResponse({'cars': 'idle'})

def email(request):
    def email_address():
        return request.GET.get('address')

    if email_address():
        text = 'Im trying to send an email to {}'.format(email_address())
        status, msg = SendgridEmail().send_to(email_address())
        return HttpResponse('<h1>{text}</h1><p>status: {status}</p><p>return message: {msg}</p>'.format(**locals()))
    else:
        return HttpResponse("<h1>Add an address param please!</h1>")
