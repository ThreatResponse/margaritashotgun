import pytest
import logging
import margaritashotgun
from margaritashotgun.exceptions import NoConfigurationError

def test_set_stream_handler():
    name = 'unittest'
    level = logging.DEBUG
    fmt = "%(message)s"
    margaritashotgun.set_stream_logger(name, level, format_string=fmt)
    logger = logging.getLogger(name)
    assert logger.name == name
    assert logger.level == level

    name = 'defaults'
    margaritashotgun.set_stream_logger(name)
    logger = logging.getLogger(name)
    assert logger.name == name
    assert logger.level == logging.INFO

def test_create_client():
    with pytest.raises(NoConfigurationError):
        margaritashotgun.client()

