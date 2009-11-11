import lamson.queue as queue
import pytyrant

archive = pytyrant.PyTyrant.open('127.0.0.1', 1978)

def enqueue(message):

    """
    Message is the final version of the email sent
    to the entire group.
    """

    links_q = queue.Queue("run/archive")
    links_q.push(message)
