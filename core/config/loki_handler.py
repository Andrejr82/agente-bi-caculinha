import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from loki_client import LokiClient

class LokiHandler(logging.Handler):
    """
    A logging handler that sends logs to a Loki server.
    """

    def __init__(self, host, port, tags=None):
        super().__init__()
        self.client = LokiClient(f"http://{host}:{port}/loki/api/v1/push", tags=tags)

    def emit(self, record):
        log_entry = self.format(record)
        self.client.push(log_entry)

def setup_loki_handler(host, port, tags=None):
    """
    Sets up a Loki handler for the root logger.
    """
    queue = Queue(-1)  # No limit on queue size
    handler = LokiHandler(host, port, tags)
    queue_handler = QueueHandler(queue)
    listener = QueueListener(queue, handler)

    root_logger = logging.getLogger()
    root_logger.addHandler(queue_handler)

    listener.start()
    return listener
