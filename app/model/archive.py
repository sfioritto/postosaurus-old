import lamson.queue as queue

def enqueue(message):
    """
    Message is the final version of the email sent
    to the entire group.
    """
    links_q = queue.Queue("run/archive")
    links_q.push(message)
