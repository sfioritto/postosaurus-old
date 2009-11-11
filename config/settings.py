# This file contains python variables that configure Lamson for email processing.
import logging
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'webapp.settings'

relay_config = {'host': 'localhost', 'port': 8825}

receiver_config = {'host': '0.0.0.0', 'port': 25}

queue_config = {'queue' : 'run/links', 'sleep' : 10}

handlers = ['app.handlers.admin']

queue_handlers = ['app.handlers.links']

router_defaults = {'host': 'postosaurus\\.com',
    'list_name': '[a-zA-Z0-9\.]+',
}

template_config = {'dir': 'app', 'module': 'templates'}

# the config/boot.py will turn these values into variables set in settings
