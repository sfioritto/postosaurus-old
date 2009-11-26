# This file contains python variables that configure Lamson for email processing.
import logging
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'webapp.settings'

from app.model import confirm

relay_config = {'host': 'localhost', 'port': 8825}

receiver_config = {'host': '0.0.0.0', 'port': 25}

queue_config = {'queue' : 'run/work', 'sleep' : 10}

error_config = {'queue' : 'run/error', 'sleep' : 10}

handlers = ['app.handlers.admin']

queue_handlers = ['app.handlers.queue']

router_defaults = {'host': 'postosaurus\\.com',
    'list_name': '[a-zA-Z0-9\.]+',
}

template_config = {'dir': 'webapp', 'module': 'templates'}

CONFIRM_STORAGE = confirm.JoinConfirmStorage()
CONFIRM = confirm.ConfirmationEngine(CONFIRM_STORAGE)

# the config/boot.py will turn these values into variables set in settings
