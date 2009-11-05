# This file contains python variables that configure Lamson for email processing.
import logging
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'webapp.settings'

relay_config = {'host': 'localhost', 'port': 8025}

receiver_config = {'host': 'localhost', 'port': 8823}

handlers = ['app.handlers.admin']

router_defaults = {'host': 'postosaurus\\.com',
    'list_name': '[a-zA-Z0-9\.]+',
    'id_number': '[a-z0-9]+',
}

template_config = {'dir': 'app', 'module': 'templates'}

# the config/boot.py will turn these values into variables set in settings
