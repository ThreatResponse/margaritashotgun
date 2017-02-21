__author__ = 'Joel Ferrier'
__version__ = '0.4.0'

import logging
from margaritashotgun.client import Client


def set_stream_logger(name='margaritashotgun', level=logging.INFO,
                      format_string=None):
    """
    Add a stream handler for the provided name and level to the logging module.

        >>> import margaritashotgun
        >>> margaritashotgun.set_stream_logger('marsho', logging.DEBUG)

    :type name: string
    :param name: Log name
    :type level: int
    :param level: Logging level
    :type format_string: str
    :param format_string: Log message format
    """

    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    time_format = "%Y-%m-%dT%H:%M:%S"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(format_string, time_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    paramiko_log_level = logging.CRITICAL
    paramiko_log = logging.getLogger('paramiko')
    paramiko_log.setLevel(paramiko_log_level)
    paramiko_handler = logging.StreamHandler()
    paramiko_handler.setLevel(paramiko_log_level)
    paramiko_handler.setFormatter(formatter)
    paramiko_log.addHandler(paramiko_handler)

def client(*args, **kwargs):
    """
    Creates a client to orchestrate LiME memory capture

    See :py:meth:`margaritashotgun.client.Client`
    """
    return Client(*args, **kwargs)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger('margaritashotgun').addHandler(NullHandler())
