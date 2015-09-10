#!/usr/bin/env python
# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idlecars.settings")

    from django.core.management import execute_from_command_line

    try:
        is_unit_test = sys.argv.index('test') == 1
        if is_unit_test and os.getenv('DJANGO_SETTINGS_MODULE', '') != 'idlecars.local_settings':
            print 'Don\'t ever run unit tests on anything other than your development environment.'
            print 'Make sure you have an env variable DJANGO_SETTINGS_MODULE=idlecars.local_settings.'
            exit(1)
    except ValueError:
        pass

    execute_from_command_line(sys.argv)
