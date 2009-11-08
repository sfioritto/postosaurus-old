import re
import lamson.queue as queue
from webapp.postosaurus.models import *


def enqueue(message):
    """
    Message is the final version of the email sent
    to the entire group.
    """
    links_q = queue.Queue("run/links")
    links_q.push(message)


