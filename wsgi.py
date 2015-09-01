"""
WSGI config for web_site project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""

import os
import sys

sys.stdout = sys.stderr

from os.path import abspath, dirname

from django.core.handlers.wsgi import WSGIHandler

sys.path.insert(0, abspath(dirname(__file__)))
os.environ["DJANGO_SETTINGS_MODULE"] = "settings_admin" #your settings module

application = WSGIHandler()


# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
